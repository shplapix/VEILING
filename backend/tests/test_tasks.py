import asyncio
import re
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.enums import LotCategory, LotStatus
from app.models.lot import Lot
from app.models.price_tick import PriceTick
from app.schemas.ws import LotExpiredEvent, LotTakenEvent, PriceTickEvent
from app.tasks.auction import process_auction_ticks, process_auction_ticks_async


async def _create_active_lot(
    session: AsyncSession,
    *,
    start_price: Decimal = Decimal("100000.00"),
    floor_price: Decimal = Decimal("50000.00"),
    current_price: Decimal = Decimal("80000.00"),
    step_amount: Decimal = Decimal("5000.00"),
    interval_seconds: int = 60,
    status: LotStatus = LotStatus.ACTIVE,
    next_drop_offset_seconds: int = -10,
) -> Lot:
    lot = Lot(
        title="Raf Simons AW01 Riot Bomber",
        brand="Raf Simons",
        designer="Raf Simons",
        season="AW",
        year=2001,
        category=LotCategory.OUTERWEAR,
        subcategory="Bomber",
        tagged_size="50",
        fits_like="Oversized 50",
        measurements={"pit_to_pit": 62, "length": 70},
        materials={"outer": "cotton", "lining": "cupro"},
        condition_rating=10,
        condition_details="Museum archive condition",
        country_of_origin="Belgium",
        start_price=start_price,
        floor_price=floor_price,
        current_price=current_price,
        step_amount=step_amount,
        interval_seconds=interval_seconds,
        status=status,
        next_drop_at=datetime.now(UTC) + timedelta(seconds=next_drop_offset_seconds),
    )
    session.add(lot)
    await session.commit()
    await session.refresh(lot)
    return lot


async def test_process_auction_ticks_idempotency(db_session: AsyncSession) -> None:
    lot = await _create_active_lot(
        db_session,
        current_price=Decimal("80000.00"),
        step_amount=Decimal("5000.00"),
        floor_price=Decimal("50000.00"),
    )

    first_run = await process_auction_ticks_async(db_session)
    assert first_run["ticks_processed"] == 1
    assert first_run["expired_processed"] == 0

    await db_session.refresh(lot)
    assert lot.current_price == Decimal("75000.00")
    assert lot.next_drop_at is not None
    lot_next_drop = (
        lot.next_drop_at if lot.next_drop_at.tzinfo else lot.next_drop_at.replace(tzinfo=UTC)
    )
    assert lot_next_drop > datetime.now(UTC)

    query_ticks = select(PriceTick).where(PriceTick.lot_id == lot.id)
    ticks = (await db_session.execute(query_ticks)).scalars().all()
    assert len(ticks) == 1
    assert ticks[0].price == Decimal("75000.00")

    second_run = await process_auction_ticks_async(db_session)
    assert second_run["ticks_processed"] == 0
    assert second_run["expired_processed"] == 0

    await db_session.refresh(lot)
    assert lot.current_price == Decimal("75000.00")

    ticks_after = (await db_session.execute(query_ticks)).scalars().all()
    assert len(ticks_after) == 1


async def test_process_auction_ticks_floor_price_boundary(
    db_session: AsyncSession,
) -> None:
    lot = await _create_active_lot(
        db_session,
        current_price=Decimal("52000.00"),
        floor_price=Decimal("50000.00"),
        step_amount=Decimal("5000.00"),
    )

    result = await process_auction_ticks_async(db_session)
    assert result["ticks_processed"] == 1

    await db_session.refresh(lot)
    assert lot.current_price == Decimal("50000.00")
    assert lot.status == LotStatus.ACTIVE


async def test_process_auction_ticks_expires_when_at_floor_price(
    db_session: AsyncSession,
) -> None:
    lot = await _create_active_lot(
        db_session,
        current_price=Decimal("50000.00"),
        floor_price=Decimal("50000.00"),
        step_amount=Decimal("5000.00"),
    )

    result = await process_auction_ticks_async(db_session)
    assert result["expired_processed"] == 1
    assert result["ticks_processed"] == 0

    await db_session.refresh(lot)
    assert lot.status == LotStatus.EXPIRED


async def test_process_auction_ticks_ignores_draft_or_taken_lots(
    db_session: AsyncSession,
) -> None:
    lot_draft = await _create_active_lot(db_session, status=LotStatus.DRAFT)
    lot_taken = await _create_active_lot(db_session, status=LotStatus.TAKEN)

    result = await process_auction_ticks_async(db_session)
    assert result["ticks_processed"] == 0
    assert result["expired_processed"] == 0

    await db_session.refresh(lot_draft)
    assert lot_draft.status == LotStatus.DRAFT

    await db_session.refresh(lot_taken)
    assert lot_taken.status == LotStatus.TAKEN


def test_process_auction_ticks_celery_task_wrapper(
    monkeypatch: pytest.MonkeyPatch,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    monkeypatch.setattr("app.tasks.auction.async_session_maker", db_session_factory)

    async def _setup_lot() -> Lot:
        async with db_session_factory() as session:
            return await _create_active_lot(
                session,
                current_price=Decimal("70000.00"),
                step_amount=Decimal("5000.00"),
                floor_price=Decimal("50000.00"),
            )

    lot = asyncio.run(_setup_lot())
    result = process_auction_ticks()
    assert isinstance(result, dict)
    assert result["ticks_processed"] == 1
    assert result["expired_processed"] == 0

    async def _verify() -> None:
        async with db_session_factory() as session:
            query = select(Lot).where(Lot.id == lot.id)
            updated = (await session.execute(query)).scalar_one()
            assert updated.current_price == Decimal("65000.00")
            query_ticks = select(PriceTick).where(PriceTick.lot_id == lot.id)
            ticks = (await session.execute(query_ticks)).scalars().all()
            assert len(ticks) == 1
            assert ticks[0].price == Decimal("65000.00")

    asyncio.run(_verify())


def test_ws_event_datetime_format_z_suffix() -> None:
    sample_id = uuid.uuid4()
    now_naive = datetime(2026, 10, 24, 18, 5, 0, 123456)
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    tick_event = PriceTickEvent(
        event="PRICE_TICK",
        lot_id=sample_id,
        current_price=Decimal("95000.00"),
        floor_price=Decimal("50000.00"),
        step_amount=Decimal("5000.00"),
        next_drop_at=now_naive,
    )
    tick_dict = tick_event.to_dict()
    assert iso_pattern.match(str(tick_dict["next_drop_at"]))
    assert str(tick_dict["next_drop_at"]) == "2026-10-24T18:05:00Z"

    taken_event = LotTakenEvent(
        event="LOT_TAKEN",
        lot_id=sample_id,
        final_price=Decimal("90000.00"),
        taken_at=now_naive,
        savings_percentage=10,
    )
    taken_dict = taken_event.to_dict()
    assert iso_pattern.match(str(taken_dict["taken_at"]))
    assert str(taken_dict["taken_at"]) == "2026-10-24T18:05:00Z"

    expired_event = LotExpiredEvent(
        event="LOT_EXPIRED",
        lot_id=sample_id,
        floor_price=Decimal("50000.00"),
        expired_at=now_naive,
    )
    expired_dict = expired_event.to_dict()
    assert iso_pattern.match(str(expired_dict["expired_at"]))
    assert str(expired_dict["expired_at"]) == "2026-10-24T18:05:00Z"
