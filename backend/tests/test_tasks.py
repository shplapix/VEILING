from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.enums import LotCategory, LotStatus
from app.models.lot import Lot
from app.models.price_tick import PriceTick
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
    result = process_auction_ticks()
    assert isinstance(result, dict)
    assert "ticks_processed" in result
    assert "expired_processed" in result
