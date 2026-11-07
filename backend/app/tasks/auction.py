import asyncio
import concurrent.futures
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, TypeVar, cast

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.redis import publish_message
from app.models.enums import LotStatus
from app.models.lot import Lot
from app.models.price_tick import PriceTick
from app.schemas.ws import LotExpiredEvent, PriceTickEvent, serialize_auction_event
from app.tasks.celery_app import celery_app

_task_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    bind=_task_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

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


async def bump_overflow_closed_lots(
    session: AsyncSession,
    now: datetime,
    max_closed: int = 8,
) -> int:
    query = (
        select(Lot)
        .where(Lot.status.in_([LotStatus.EXPIRED, LotStatus.TAKEN]))
        .order_by(
            func.coalesce(Lot.taken_at, Lot.updated_at, Lot.created_at).desc(),
            Lot.id.desc(),
        )
    )
    closed_lots = list((await session.execute(query)).scalars().all())
    if len(closed_lots) <= max_closed:
        return 0

    bumped_count = 0
    overflow_lots = closed_lots[max_closed:]
    for lot in overflow_lots:
        if lot.status == LotStatus.EXPIRED:
            lot.status = LotStatus.DRAFT
            lot.current_price = lot.start_price
            lot.started_at = None
            lot.next_drop_at = None
            lot.taken_at = None
            lot.winner_id = None
            lot.final_price = None
            lot.updated_at = now
            bumped_count += 1

    return bumped_count


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
    fresh_query = (
        select(Lot)
        .options(selectinload(Lot.images))
        .where(Lot.status.in_([LotStatus.DRAFT, LotStatus.SCHEDULED]))
        .order_by(Lot.updated_at.asc(), Lot.created_at.asc())
        .limit(needed)
    )
    candidates = list((await session.execute(fresh_query)).scalars().all())
    if not candidates:
        return 0

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

    return activated_count


async def rebalance_auction_lots(
    session: AsyncSession,
    now: datetime,
    redis_client: Any | None = None,
    target_active: int = 6,
    max_closed: int = 8,
) -> dict[str, int]:
    bumped = await bump_overflow_closed_lots(session, now, max_closed=max_closed)
    activated = await cycle_reserve_lots(
        session, now, redis_client=redis_client, target_active=target_active
    )
    if bumped > 0 or activated > 0:
        await session.commit()
    return {"bumped": bumped, "activated": activated}


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
            "RETURNING id, floor_price, updated_at;"
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
            "RETURNING id, floor_price, updated_at;"
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
        expired_at = _parse_datetime(row.updated_at, now)
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

    if len(expired_rows) > 0:
        await rebalance_auction_lots(
            session, now, redis_client=redis_client, target_active=6, max_closed=8
        )

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
        return await rebalance_auction_lots(session, now, redis_client)

    async with async_session_maker() as new_session:
        return await rebalance_auction_lots(new_session, now, redis_client)


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
