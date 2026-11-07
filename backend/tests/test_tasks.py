import asyncio
import re
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import func, select
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


async def test_bump_overflow_closed_lots_cap_at_eight(
    db_session: AsyncSession,
) -> None:
    from app.tasks.auction import bump_overflow_closed_lots

    now = datetime.now(UTC)
    lots: list[Lot] = []
    for i in range(10):
        lot = await _create_active_lot(
            db_session,
            status=LotStatus.EXPIRED,
            current_price=Decimal("50000.00"),
            floor_price=Decimal("50000.00"),
        )
        lot.updated_at = now - timedelta(minutes=(10 - i) * 5)
        lots.append(lot)
    await db_session.commit()

    bumped = await bump_overflow_closed_lots(db_session, now, max_closed=8)
    assert bumped == 2

    query_closed = (
        select(Lot)
        .where(Lot.status.in_([LotStatus.EXPIRED, LotStatus.TAKEN]))
        .order_by(Lot.updated_at.desc())
    )
    closed_after = list((await db_session.execute(query_closed)).scalars().all())
    assert len(closed_after) == 8

    query_draft = select(Lot).where(Lot.status == LotStatus.DRAFT)
    draft_after = list((await db_session.execute(query_draft)).scalars().all())
    assert len(draft_after) == 2
    for d_lot in draft_after:
        assert d_lot.current_price == d_lot.start_price
        assert d_lot.started_at is None
        assert d_lot.next_drop_at is None
        assert d_lot.taken_at is None
        assert d_lot.winner_id is None
        assert d_lot.final_price is None


async def test_rebalance_and_fifo_rotation_active_to_closed_to_queue(
    db_session: AsyncSession,
) -> None:
    from app.tasks.auction import rebalance_auction_lots

    now = datetime.now(UTC)
    active_lots: list[Lot] = []
    for _ in range(5):
        lot = await _create_active_lot(
            db_session,
            status=LotStatus.ACTIVE,
            current_price=Decimal("80000.00"),
        )
        active_lots.append(lot)

    closed_lots: list[Lot] = []
    for i in range(9):
        lot = await _create_active_lot(
            db_session,
            status=LotStatus.EXPIRED,
            current_price=Decimal("50000.00"),
            floor_price=Decimal("50000.00"),
        )
        lot.updated_at = now - timedelta(minutes=(10 - i) * 5)
        closed_lots.append(lot)

    queue_lot = await _create_active_lot(
        db_session,
        status=LotStatus.DRAFT,
        current_price=Decimal("100000.00"),
    )
    queue_lot.updated_at = now - timedelta(hours=2)
    await db_session.commit()

    result = await rebalance_auction_lots(db_session, now, target_active=6, max_closed=8)
    assert result["bumped"] == 1
    assert result["activated"] == 1

    query_active = select(func.count(Lot.id)).where(Lot.status == LotStatus.ACTIVE)
    active_count = (await db_session.execute(query_active)).scalar_one()
    assert active_count == 6

    query_closed = select(func.count(Lot.id)).where(
        Lot.status.in_([LotStatus.EXPIRED, LotStatus.TAKEN])
    )
    closed_count = (await db_session.execute(query_closed)).scalar_one()
    assert closed_count == 8

    await db_session.refresh(queue_lot)
    assert queue_lot.status == LotStatus.ACTIVE
    assert queue_lot.current_price == queue_lot.start_price


async def test_bump_overflow_closed_lots_preserves_taken_lots(
    db_session: AsyncSession,
) -> None:
    from app.tasks.auction import bump_overflow_closed_lots

    now = datetime.now(UTC)
    for i in range(8):
        lot = await _create_active_lot(
            db_session,
            status=LotStatus.EXPIRED,
            current_price=Decimal("50000.00"),
            floor_price=Decimal("50000.00"),
        )
        lot.updated_at = now - timedelta(minutes=(8 - i) * 5)

    taken_lot = await _create_active_lot(
        db_session,
        status=LotStatus.TAKEN,
        current_price=Decimal("70000.00"),
    )
    taken_lot.taken_at = now - timedelta(hours=1)
    taken_lot.final_price = Decimal("70000.00")
    await db_session.commit()

    bumped = await bump_overflow_closed_lots(db_session, now, max_closed=8)
    assert bumped == 0

    await db_session.refresh(taken_lot)
    assert taken_lot.status == LotStatus.TAKEN
    assert taken_lot.taken_at is not None
    assert taken_lot.final_price == Decimal("70000.00")
