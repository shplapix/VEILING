import asyncio
import concurrent.futures
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, TypeVar, cast

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import async_session_maker
from app.core.redis import publish_message
from app.models.enums import LotStatus
from app.models.lot import Lot
from app.models.price_tick import PriceTick
from app.schemas.ws import LotExpiredEvent, PriceTickEvent, serialize_auction_event
from app.tasks.celery_app import celery_app

F = TypeVar("F", bound=Callable[..., Any])


def task(*args: Any, **kwargs: Any) -> Callable[[F], F]:
    return cast(Callable[[F], F], celery_app.task(*args, **kwargs))


def _parse_datetime(raw: object, fallback: datetime) -> datetime:
    if isinstance(raw, datetime):
        return raw if raw.tzinfo else raw.replace(tzinfo=UTC)
    if isinstance(raw, str):
        try:
            parsed = datetime.fromisoformat(raw)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            return fallback
    return fallback


async def cycle_reserve_lots(
    session: AsyncSession,
    now: datetime,
    redis_client: Any | None = None,
    target_active: int = 6,
) -> int:
    active_count_res = await session.execute(
        select(func.count()).select_from(Lot).where(Lot.status == LotStatus.ACTIVE)
    )
    active_count = active_count_res.scalar() or 0
    if active_count >= target_active:
        return 0

    needed = target_active - active_count
    candidates: list[Lot] = []

    fresh_query = (
        select(Lot)
        .options(selectinload(Lot.images))
        .where(Lot.status.in_([LotStatus.DRAFT, LotStatus.SCHEDULED]))
        .order_by(Lot.created_at.asc())
        .limit(needed)
    )
    fresh_lots = list((await session.execute(fresh_query)).scalars().all())
    candidates.extend(fresh_lots)

    if len(candidates) < needed:
        still_needed = needed - len(candidates)
        expired_query = (
            select(Lot)
            .options(selectinload(Lot.images))
            .where(Lot.status == LotStatus.EXPIRED)
            .order_by(Lot.updated_at.asc(), Lot.created_at.asc())
            .limit(still_needed)
        )
        expired_lots = list((await session.execute(expired_query)).scalars().all())
        candidates.extend(expired_lots)

    if len(candidates) < needed:
        still_needed = needed - len(candidates)
        taken_query = (
            select(Lot)
            .options(selectinload(Lot.images))
            .where(Lot.status == LotStatus.TAKEN)
            .order_by(Lot.taken_at.asc(), Lot.updated_at.asc())
            .limit(still_needed)
        )
        taken_lots = list((await session.execute(taken_query)).scalars().all())
        candidates.extend(taken_lots)

    activated_count = 0
    for idx, lot in enumerate(candidates):
        lot.status = LotStatus.ACTIVE
        lot.current_price = lot.start_price
        lot.started_at = now
        stagger = (idx * 15) % max(15, lot.interval_seconds)
        lot.next_drop_at = now + timedelta(seconds=max(20, lot.interval_seconds - stagger))
        lot.taken_at = None
        lot.winner_id = None
        lot.final_price = None
        lot.updated_at = now
        activated_count += 1

        tick_event = PriceTickEvent(
            event="PRICE_TICK",
            lot_id=lot.id,
            current_price=lot.current_price,
            floor_price=lot.floor_price,
            step_amount=lot.step_amount,
            next_drop_at=lot.next_drop_at,
        )
        await publish_message(
            "auction_events",
            serialize_auction_event(tick_event),
            redis_client,
        )

    if activated_count > 0:
        await session.commit()

    return activated_count


async def _execute_auction_ticks(
    session: AsyncSession,
    now: datetime,
    redis_client: Any | None = None,
) -> dict[str, int]:
    bind = session.get_bind()
    dialect = bind.dialect.name if bind else "postgresql"

    if dialect == "postgresql":
        expire_sql = text(
            "UPDATE lots "
            "SET status = 'EXPIRED', "
            "    updated_at = clock_timestamp() "
            "WHERE status = 'ACTIVE' "
            "  AND next_drop_at <= clock_timestamp() "
            "  AND current_price <= floor_price "
            "RETURNING id, floor_price, next_drop_at;"
        )
        tick_sql = text(
            "UPDATE lots "
            "SET current_price = GREATEST(floor_price, current_price - step_amount), "
            "    next_drop_at = clock_timestamp() + (interval_seconds * INTERVAL '1 second'), "
            "    updated_at = clock_timestamp() "
            "WHERE status = 'ACTIVE' "
            "  AND next_drop_at <= clock_timestamp() "
            "  AND current_price > floor_price "
            "RETURNING id, current_price, floor_price, step_amount, next_drop_at;"
        )
    else:
        expire_sql = text(
            "UPDATE lots "
            "SET status = 'EXPIRED', "
            "    updated_at = CURRENT_TIMESTAMP "
            "WHERE status = 'ACTIVE' "
            "  AND next_drop_at <= CURRENT_TIMESTAMP "
            "  AND current_price <= floor_price "
            "RETURNING id, floor_price, next_drop_at;"
        )
        tick_sql = text(
            "UPDATE lots "
            "SET current_price = MAX(floor_price, current_price - step_amount), "
            "    next_drop_at = "
            "datetime(CURRENT_TIMESTAMP, '+' || interval_seconds || ' seconds'), "
            "    updated_at = CURRENT_TIMESTAMP "
            "WHERE status = 'ACTIVE' "
            "  AND next_drop_at <= CURRENT_TIMESTAMP "
            "  AND current_price > floor_price "
            "RETURNING id, current_price, floor_price, step_amount, next_drop_at;"
        )

    expire_result = await session.execute(expire_sql)
    expired_rows = expire_result.fetchall()

    for row in expired_rows:
        row_id = row.id if isinstance(row.id, uuid.UUID) else uuid.UUID(str(row.id))
        floor_price = Decimal(str(row.floor_price))
        expired_at = _parse_datetime(row.next_drop_at, now)
        expired_event = LotExpiredEvent(
            event="LOT_EXPIRED",
            lot_id=row_id,
            floor_price=floor_price,
            expired_at=expired_at,
        )
        await publish_message(
            "auction_events",
            serialize_auction_event(expired_event),
            redis_client,
        )

    tick_result = await session.execute(tick_sql)
    ticked_rows = tick_result.fetchall()

    for row in ticked_rows:
        row_id = row.id if isinstance(row.id, uuid.UUID) else uuid.UUID(str(row.id))
        current_price = Decimal(str(row.current_price))
        floor_price = Decimal(str(row.floor_price))
        step_amount = Decimal(str(row.step_amount))
        next_drop_at = _parse_datetime(row.next_drop_at, now + timedelta(seconds=60))

        tick = PriceTick(
            lot_id=row_id,
            price=current_price,
        )
        session.add(tick)

        tick_event = PriceTickEvent(
            event="PRICE_TICK",
            lot_id=row_id,
            current_price=current_price,
            floor_price=floor_price,
            step_amount=step_amount,
            next_drop_at=next_drop_at,
        )
        await publish_message(
            "auction_events",
            serialize_auction_event(tick_event),
            redis_client,
        )

    await session.commit()

    return {
        "ticks_processed": len(ticked_rows),
        "expired_processed": len(expired_rows),
    }


async def process_auction_ticks_async(
    session: AsyncSession | None = None,
    redis_client: Any | None = None,
) -> dict[str, int]:
    now = datetime.now(UTC)
    if session is not None:
        return await _execute_auction_ticks(session, now, redis_client)

    async with async_session_maker() as new_session:
        return await _execute_auction_ticks(new_session, now, redis_client)


@task(name="app.tasks.auction.process_auction_ticks")
def process_auction_ticks(session: AsyncSession | None = None) -> dict[str, int]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(lambda: asyncio.run(process_auction_ticks_async(session)))
            return future.result()
    return asyncio.run(process_auction_ticks_async(session))


async def process_cycle_lots_async(
    session: AsyncSession | None = None,
    redis_client: Any | None = None,
) -> dict[str, int]:
    now = datetime.now(UTC)
    if session is not None:
        count = await cycle_reserve_lots(session, now, redis_client)
        return {"cycled_processed": count}

    async with async_session_maker() as new_session:
        count = await cycle_reserve_lots(new_session, now, redis_client)
        return {"cycled_processed": count}


@task(name="app.tasks.auction.cycle_auction_lots")
def cycle_auction_lots(session: AsyncSession | None = None) -> dict[str, int]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(lambda: asyncio.run(process_cycle_lots_async(session)))
            return future.result()
    return asyncio.run(process_cycle_lots_async(session))
