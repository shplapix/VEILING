import asyncio
import concurrent.futures
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, TypeVar, cast

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.core.redis import publish_message
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
            "SET status = 'EXPIRED' "
            "WHERE status = 'ACTIVE' "
            "  AND next_drop_at <= clock_timestamp() "
            "  AND current_price <= floor_price "
            "RETURNING id, floor_price, next_drop_at;"
        )
        tick_sql = text(
            "UPDATE lots "
            "SET current_price = GREATEST(floor_price, current_price - step_amount), "
            "    next_drop_at = clock_timestamp() + (interval_seconds * INTERVAL '1 second') "
            "WHERE status = 'ACTIVE' "
            "  AND next_drop_at <= clock_timestamp() "
            "  AND current_price > floor_price "
            "RETURNING id, current_price, floor_price, step_amount, next_drop_at;"
        )
    else:
        expire_sql = text(
            "UPDATE lots "
            "SET status = 'EXPIRED' "
            "WHERE status = 'ACTIVE' "
            "  AND next_drop_at <= CURRENT_TIMESTAMP "
            "  AND current_price <= floor_price "
            "RETURNING id, floor_price, next_drop_at;"
        )
        tick_sql = text(
            "UPDATE lots "
            "SET current_price = MAX(floor_price, current_price - step_amount), "
            "    next_drop_at = datetime(CURRENT_TIMESTAMP, '+' || interval_seconds || ' seconds') "
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
