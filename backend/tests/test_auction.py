import asyncio
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.ws import manager
from app.core.redis import (
    publish_message,
    register_local_listener,
    unregister_local_listener,
)
from app.main import app
from app.models.enums import LotCategory, LotStatus
from app.models.lot import Lot
from app.models.order import Order
from app.models.user import User


async def create_test_lot(
    session: AsyncSession,
    *,
    title: str = "Helmut Lang AW99 Astro Jacket",
    brand: str = "Helmut Lang",
    designer: str = "Helmut Lang",
    season: str = "AW",
    year: int = 1999,
    category: LotCategory = LotCategory.OUTERWEAR,
    subcategory: str = "Astro Jacket",
    tagged_size: str = "48",
    fits_like: str = "Medium",
    measurements: dict[str, Any] | None = None,
    materials: dict[str, Any] | None = None,
    condition_rating: int = 9,
    condition_details: str = "Museum preservation archive piece",
    country_of_origin: str = "Italy",
    start_price: Decimal = Decimal("100000.00"),
    floor_price: Decimal = Decimal("50000.00"),
    current_price: Decimal = Decimal("80000.00"),
    step_amount: Decimal = Decimal("5000.00"),
    interval_seconds: int = 60,
    status: LotStatus = LotStatus.ACTIVE,
    next_drop_at: datetime | None = None,
) -> Lot:
    lot = Lot(
        title=title,
        brand=brand,
        designer=designer,
        season=season,
        year=year,
        category=category,
        subcategory=subcategory,
        tagged_size=tagged_size,
        fits_like=fits_like,
        measurements=measurements or {"pit_to_pit": 54, "length": 65},
        materials=materials or {"outer": "cotton", "lining": "cupro"},
        condition_rating=condition_rating,
        condition_details=condition_details,
        country_of_origin=country_of_origin,
        start_price=start_price,
        floor_price=floor_price,
        current_price=current_price,
        step_amount=step_amount,
        interval_seconds=interval_seconds,
        status=status,
        next_drop_at=next_drop_at,
    )
    session.add(lot)
    await session.commit()
    await session.refresh(lot)
    return lot


async def test_race_condition_take_lot_20_concurrent_requests(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    lot = await create_test_lot(
        db_session,
        start_price=Decimal("100000.00"),
        floor_price=Decimal("50000.00"),
        current_price=Decimal("80000.00"),
    )

    async def _send_take(index: int) -> int:
        res = await client.post(
            f"/api/v1/lots/{lot.id}/take",
            json={
                "buyer_contact": f"buyer_{index}@archive.com",
                "shipping_address": {
                    "full_name": f"Buyer {index}",
                    "city": "Kyiv",
                    "address_line": "Khreshchatyk 1",
                },
            },
        )
        return res.status_code

    results = await asyncio.gather(*[_send_take(i) for i in range(20)])

    success_count = sum(1 for code in results if code == 200)
    conflict_count = sum(1 for code in results if code == 409)

    assert success_count == 1
    assert conflict_count == 19

    query_orders = select(func.count(Order.id)).where(Order.lot_id == lot.id)
    order_count = (await db_session.execute(query_orders)).scalar_one()
    assert order_count == 1

    query_order = select(Order).where(Order.lot_id == lot.id)
    order = (await db_session.execute(query_order)).scalar_one()
    assert order.claim_code.startswith("V-")
    assert order.final_price == Decimal("80000.00")
    assert order.savings_from_ceiling == Decimal("20000.00")
    assert order.savings_percentage == 20

    await db_session.refresh(lot)
    assert lot.status == LotStatus.TAKEN
    assert lot.taken_at is not None
    assert lot.final_price == Decimal("80000.00")


async def test_take_lot_nonexistent_returns_404(client: AsyncClient) -> None:
    non_existent_id = uuid.uuid4()
    response = await client.post(f"/api/v1/lots/{non_existent_id}/take")
    assert response.status_code == 404
    assert response.json()["detail"] == "Lot not found"


async def test_take_lot_already_taken_returns_409(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    lot = await create_test_lot(db_session, status=LotStatus.TAKEN)
    response = await client.post(f"/api/v1/lots/{lot.id}/take")
    assert response.status_code == 409
    assert response.json()["detail"] == "Цю річ уже забрав інший покупець"


async def test_take_lot_expired_returns_409(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    lot = await create_test_lot(db_session, status=LotStatus.EXPIRED)
    response = await client.post(f"/api/v1/lots/{lot.id}/take")
    assert response.status_code == 409
    assert response.json()["detail"] == "Цю річ уже забрав інший покупець"


async def test_take_lot_draft_returns_409(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    lot = await create_test_lot(db_session, status=LotStatus.DRAFT)
    response = await client.post(f"/api/v1/lots/{lot.id}/take")
    assert response.status_code == 409
    assert response.json()["detail"] == "Цю річ уже забрав інший покупець"


async def test_take_lot_authenticated_user_sets_winner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "buyer@archive.fashion",
            "password": "Password123!",
            "role": "CUSTOMER",
            "full_name": "Valued Buyer",
        },
    )
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]

    lot = await create_test_lot(db_session)
    response = await client.post(
        f"/api/v1/lots/{lot.id}/take",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claim_code"].startswith("V-")

    query_user = select(User).where(User.email == "buyer@archive.fashion")
    user = (await db_session.execute(query_user)).scalar_one()

    await db_session.refresh(lot)
    assert lot.winner_id == user.id

    query_order = select(Order).where(Order.lot_id == lot.id)
    order = (await db_session.execute(query_order)).scalar_one()
    assert order.user_id == user.id
    assert order.buyer_contact == "buyer@archive.fashion"


async def test_take_lot_anonymous_user_succeeds(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    lot = await create_test_lot(db_session)
    response = await client.post(f"/api/v1/lots/{lot.id}/take")
    assert response.status_code == 200
    data = response.json()
    assert data["claim_code"].startswith("V-")
    assert data["order"]["status"] == "PAID"

    await db_session.refresh(lot)
    assert lot.winner_id is None


async def test_get_lot_and_list_lots(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    lot1 = await create_test_lot(db_session, title="Lot Alpha", status=LotStatus.ACTIVE)
    lot2 = await create_test_lot(db_session, title="Lot Beta", status=LotStatus.TAKEN)

    res_get = await client.get(f"/api/v1/lots/{lot1.id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == str(lot1.id)
    assert res_get.json()["title"] == "Lot Alpha"

    res_list = await client.get("/api/v1/lots")
    assert res_list.status_code == 200
    lots = res_list.json()
    lot_ids = [item["id"] for item in lots]
    assert str(lot1.id) in lot_ids
    assert str(lot2.id) in lot_ids

    res_filtered = await client.get("/api/v1/lots?status=ACTIVE")
    assert res_filtered.status_code == 200
    filtered_lots = res_filtered.json()
    filtered_ids = [item["id"] for item in filtered_lots]
    assert str(lot1.id) in filtered_ids
    assert str(lot2.id) not in filtered_ids


def test_websocket_auction_events_broadcast() -> None:
    with (
        TestClient(app) as test_client,
        test_client.websocket_connect("/api/v1/ws") as websocket,
    ):
        sample_payload = (
            '{"event": "PRICE_TICK", "lot_id": "11111111-1111-1111-1111-111111111111", '
            '"current_price": 95000.0, "floor_price": 50000.0, "step_amount": 5000.0, '
            '"next_drop_at": "2026-10-24T18:05:00Z"}'
        )
        asyncio.run(publish_message("auction_events", sample_payload))
        data = websocket.receive_text()
        assert "PRICE_TICK" in data
        assert "95000" in data


def test_websocket_auction_subpath_broadcast() -> None:
    with (
        TestClient(app) as test_client,
        test_client.websocket_connect("/api/v1/ws/auction") as websocket,
    ):
        sample_payload = (
            '{"event": "PRICE_TICK", "lot_id": "22222222-2222-2222-2222-222222222222", '
            '"current_price": 85000.0, "floor_price": 40000.0, "step_amount": 5000.0, '
            '"next_drop_at": "2026-10-24T18:10:00Z"}'
        )
        asyncio.run(publish_message("auction_events", sample_payload))
        data = websocket.receive_text()
        assert "PRICE_TICK" in data
        assert "85000" in data


def test_websocket_disconnect_cleans_up() -> None:
    with TestClient(app) as test_client:
        initial_count = manager.active_count
        with test_client.websocket_connect("/api/v1/ws"):
            assert manager.active_count == initial_count + 1
        assert manager.active_count == initial_count


@pytest.mark.asyncio
async def test_publish_message_no_duplicate_local_when_redis_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str]] = []

    async def _dummy_listener(ch: str, msg: str) -> None:
        calls.append((ch, msg))

    register_local_listener(_dummy_listener)
    try:
        mock_publish = AsyncMock(return_value=True)
        monkeypatch.setattr("app.core.redis.publish_to_channel", mock_publish)
        await publish_message("auction_events", '{"event": "TEST"}')
        assert mock_publish.await_count == 1
        assert len(calls) == 0
    finally:
        unregister_local_listener(_dummy_listener)
