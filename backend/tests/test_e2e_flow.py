import asyncio
import json
import re
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.deps import get_db
from app.main import app
from app.models.enums import LotCategory, LotStatus, UserRole
from app.models.lot import Lot
from app.models.order import Order
from app.models.price_tick import PriceTick
from app.tasks.auction import process_auction_ticks


def _build_archival_lot_payload() -> dict[str, Any]:
    return {
        "title": "Helmut Lang AW99 Astro Moto Parka",
        "brand": "Helmut Lang",
        "designer": "Helmut Lang",
        "season": "Autumn/Winter 1999",
        "year": 1999,
        "collection_name": "Seance de Travail",
        "category": LotCategory.OUTERWEAR.value,
        "subcategory": "Parka",
        "tagged_size": "48",
        "fits_like": "True to size 48",
        "measurements": {
            "pit_to_pit": 58,
            "length": 84,
            "shoulders": 50,
            "sleeve": 65,
        },
        "materials": {
            "outer": "100% Ballistic Poly-Cotton",
            "lining": "Goose Down Quilted",
            "collar": "Real Shearling Fur",
        },
        "condition_rating": 10,
        "condition_details": "Museum archive condition with original straps and collar",
        "country_of_origin": "Italy",
        "provenance_notes": "Acquired from private collector in Milan",
        "seller_location": "Мілан, Італія",
        "shipping_notes": "Insured worldwide express courier",
        "start_price": "120000.00",
        "floor_price": "60000.00",
        "step_amount": "5000.00",
        "interval_seconds": 60,
        "status": LotStatus.ACTIVE.value,
        "images": [
            {
                "image_url": "http://localhost:9000/archive-lots/astro_front.jpg",
                "sort_order": 0,
                "caption": "Front view with collar up",
            },
            {
                "image_url": "http://localhost:9000/archive-lots/astro_straps.jpg",
                "sort_order": 1,
                "caption": "Internal backpack bondage straps",
            },
        ],
    }


def test_full_dutch_auction_e2e_flow(
    monkeypatch: pytest.MonkeyPatch,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    monkeypatch.setattr("app.tasks.auction.async_session_maker", db_session_factory)

    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_db

    try:
        with TestClient(app) as client:
            seller_payload = {
                "email": "curator.lang@veiling.archive",
                "password": "ArchivalCurator2026!",
                "full_name": "Олександр Коваль",
                "role": UserRole.SELLER.value,
            }
            reg_res = client.post("/api/v1/auth/register", json=seller_payload)
            assert reg_res.status_code == 201

            login_res = client.post(
                "/api/v1/auth/login",
                json={
                    "email": seller_payload["email"],
                    "password": seller_payload["password"],
                },
            )
            assert login_res.status_code == 200
            token = login_res.json()["access_token"]
            assert token
            headers = {"Authorization": f"Bearer {token}"}

            me_res = client.get("/api/v1/auth/me", headers=headers)
            assert me_res.status_code == 200
            assert me_res.json()["email"] == seller_payload["email"]
            assert me_res.json()["role"] == "SELLER"

            create_res = client.post(
                "/api/v1/lots",
                json=_build_archival_lot_payload(),
                headers=headers,
            )
            assert create_res.status_code == 201
            lot_data = create_res.json()
            lot_id = lot_data["id"]
            assert lot_data["title"] == "Helmut Lang AW99 Astro Moto Parka"
            assert lot_data["status"] == "ACTIVE"
            assert Decimal(str(lot_data["current_price"])) == Decimal("120000.00")
            assert Decimal(str(lot_data["start_price"])) == Decimal("120000.00")
            assert Decimal(str(lot_data["floor_price"])) == Decimal("60000.00")
            assert len(lot_data["images"]) == 2

            with client.websocket_connect("/api/v1/ws") as websocket:

                async def _age_lot() -> None:
                    async with db_session_factory() as session:
                        lot = await session.get(Lot, uuid.UUID(lot_id))
                        assert lot is not None
                        lot.next_drop_at = datetime.now(UTC) - timedelta(seconds=15)
                        await session.commit()

                asyncio.run(_age_lot())

                tick_result = process_auction_ticks()
                assert tick_result["ticks_processed"] == 1
                assert tick_result["expired_processed"] == 0

                raw_price_tick = websocket.receive_text()
                price_tick_event = json.loads(raw_price_tick)
                assert price_tick_event["event"] == "PRICE_TICK"
                assert price_tick_event["lot_id"] == lot_id
                assert Decimal(str(price_tick_event["current_price"])) == Decimal("115000.00")
                assert Decimal(str(price_tick_event["floor_price"])) == Decimal("60000.00")
                assert Decimal(str(price_tick_event["step_amount"])) == Decimal("5000.00")
                assert str(price_tick_event["next_drop_at"]).endswith("Z")

                take_payload = {
                    "buyer_contact": "archival.buyer@tokyo.jp",
                    "shipping_address": {
                        "recipient_name": "Kenzo Tanaka",
                        "city": "Tokyo",
                        "address": "Minato-ku, Aoyama 3-1",
                    },
                }
                take_res = client.post(f"/api/v1/lots/{lot_id}/take", json=take_payload)
                assert take_res.status_code == 200
                take_data = take_res.json()
                assert "claim_code" in take_data
                assert "order" in take_data

                claim_code = take_data["claim_code"]
                assert re.match(r"^V-2026-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$", claim_code)
                assert Decimal(str(take_data["order"]["final_price"])) == Decimal("115000.00")
                assert take_data["order"]["status"] == "PAID"
                assert take_data["order"]["claim_code"] == claim_code
                assert take_data["order"]["buyer_contact"] == "archival.buyer@tokyo.jp"

                raw_taken = websocket.receive_text()
                taken_event = json.loads(raw_taken)
                assert taken_event["event"] == "LOT_TAKEN"
                assert taken_event["lot_id"] == lot_id
                assert Decimal(str(taken_event["final_price"])) == Decimal("115000.00")
                assert taken_event["savings_percentage"] == 4
                assert str(taken_event["taken_at"]).endswith("Z")

            lookup_res = client.get(f"/api/v1/orders/lookup?code={claim_code}")
            assert lookup_res.status_code == 200
            lookup_data = lookup_res.json()
            assert lookup_data["claim_code"] == claim_code
            assert lookup_data["buyer_contact"] == "archival.buyer@tokyo.jp"
            assert lookup_data["status"] == "PAID"
            assert Decimal(str(lookup_data["final_price"])) == Decimal("115000.00")
            assert lookup_data["savings_percentage"] == 4
            assert lookup_data["lot"]["id"] == lot_id
            assert lookup_data["lot"]["title"] == "Helmut Lang AW99 Astro Moto Parka"
            assert lookup_data["lot"]["brand"] == "Helmut Lang"
            assert lookup_data["lot"]["designer"] == "Helmut Lang"
            assert lookup_data["lot"]["year"] == 1999

            padded_code = f"  {claim_code.lower()}  "
            lookup_padded = client.get(f"/api/v1/orders/lookup?code={padded_code}")
            assert lookup_padded.status_code == 200
            assert lookup_padded.json()["claim_code"] == claim_code

            ledger_res = client.get("/api/v1/orders/ledger")
            assert ledger_res.status_code == 200
            ledger = ledger_res.json()
            assert isinstance(ledger, list)

            matched_records = [r for r in ledger if r["lot_id"] == lot_id]
            assert len(matched_records) == 1
            ledger_entry = matched_records[0]

            assert Decimal(str(ledger_entry["final_price"])) == Decimal("115000.00")
            assert ledger_entry["savings_percentage"] == 4
            assert ledger_entry["claim_code"].startswith("V-2026-")
            assert ledger_entry["claim_code"].endswith("****-****")
            assert "buyer_contact" not in ledger_entry
            assert "shipping_address" not in ledger_entry
            assert "payment_reference" not in ledger_entry
            assert "user_id" not in ledger_entry
            assert ledger_entry["lot"]["title"] == "Helmut Lang AW99 Astro Moto Parka"
            assert ledger_entry["lot"]["brand"] == "Helmut Lang"

            second_take_res = client.post(
                f"/api/v1/lots/{lot_id}/take",
                json={
                    "buyer_contact": "late.buyer@london.uk",
                    "shipping_address": {
                        "recipient_name": "Late Buyer",
                        "city": "London",
                        "address": "Bond Street 1",
                    },
                },
            )
            assert second_take_res.status_code == 409
            assert second_take_res.json()["detail"] == "Цю річ уже забрав інший покупець"

            async def _verify_database_integrity() -> None:
                async with db_session_factory() as session:
                    db_lot = await session.get(Lot, uuid.UUID(lot_id))
                    assert db_lot is not None
                    assert db_lot.status == LotStatus.TAKEN
                    assert db_lot.taken_at is not None
                    assert db_lot.final_price == Decimal("115000.00")

                    query_ticks = select(PriceTick).where(PriceTick.lot_id == uuid.UUID(lot_id))
                    ticks = (await session.execute(query_ticks)).scalars().all()
                    assert len(ticks) == 1
                    assert ticks[0].price == Decimal("115000.00")

                    orders_query = select(Order).where(Order.lot_id == uuid.UUID(lot_id))
                    orders = (await session.execute(orders_query)).scalars().all()
                    assert len(orders) == 1
                    assert orders[0].claim_code == claim_code
                    assert orders[0].buyer_contact == "archival.buyer@tokyo.jp"

            asyncio.run(_verify_database_integrity())

    finally:
        app.dependency_overrides.clear()


def test_e2e_celery_task_and_websocket_broadcast(
    monkeypatch: pytest.MonkeyPatch,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    monkeypatch.setattr("app.tasks.auction.async_session_maker", db_session_factory)

    lot_id_holder: list[uuid.UUID] = []

    async def _setup() -> None:
        async with db_session_factory() as session:
            lot = Lot(
                title="Raf Simons AW02 Virginia Creeper Raglan",
                brand="Raf Simons",
                designer="Raf Simons",
                season="AW",
                year=2002,
                category=LotCategory.TOPS,
                subcategory="Sweatshirt",
                tagged_size="48",
                fits_like="Oversized 48",
                measurements={"pit_to_pit": 60, "length": 68},
                materials={"outer": "Acid Washed Cotton"},
                condition_rating=9,
                condition_details="Original collegiate print with natural distressing",
                country_of_origin="Belgium",
                start_price=Decimal("90000.00"),
                floor_price=Decimal("50000.00"),
                current_price=Decimal("80000.00"),
                step_amount=Decimal("5000.00"),
                interval_seconds=60,
                status=LotStatus.ACTIVE,
                next_drop_at=datetime.now(UTC) - timedelta(seconds=10),
            )
            session.add(lot)
            await session.commit()
            await session.refresh(lot)
            lot_id_holder.append(lot.id)

    asyncio.run(_setup())
    lot_id = lot_id_holder[0]

    with (
        TestClient(app) as test_client,
        test_client.websocket_connect("/api/v1/ws") as websocket,
    ):
        result = process_auction_ticks()
        assert result["ticks_processed"] == 1

        raw_data = websocket.receive_text()
        parsed = json.loads(raw_data)
        assert parsed["event"] == "PRICE_TICK"
        assert parsed["lot_id"] == str(lot_id)
        assert Decimal(str(parsed["current_price"])) == Decimal("75000.00")
        assert Decimal(str(parsed["floor_price"])) == Decimal("50000.00")
        assert Decimal(str(parsed["step_amount"])) == Decimal("5000.00")

    async def _verify() -> None:
        async with db_session_factory() as session:
            db_lot = await session.get(Lot, lot_id)
            assert db_lot is not None
            assert db_lot.current_price == Decimal("75000.00")

    asyncio.run(_verify())


def test_e2e_celery_task_expires_lot_and_broadcasts_websocket(
    monkeypatch: pytest.MonkeyPatch,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    monkeypatch.setattr("app.tasks.auction.async_session_maker", db_session_factory)

    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_db

    try:
        lot_id_holder: list[uuid.UUID] = []

        async def _setup() -> None:
            async with db_session_factory() as session:
                lot = Lot(
                    title="Undercover SS06 T-Shirt",
                    brand="Undercover",
                    designer="Jun Takahashi",
                    season="SS",
                    year=2006,
                    category=LotCategory.TOPS,
                    subcategory="T-Shirt",
                    tagged_size="2",
                    fits_like="Slim M",
                    measurements={"pit_to_pit": 50, "length": 65},
                    materials={"outer": "Cotton 100%"},
                    condition_rating=8,
                    condition_details="Archival graphic",
                    country_of_origin="Japan",
                    start_price=Decimal("40000.00"),
                    floor_price=Decimal("20000.00"),
                    current_price=Decimal("20000.00"),
                    step_amount=Decimal("2000.00"),
                    interval_seconds=60,
                    status=LotStatus.ACTIVE,
                    next_drop_at=datetime.now(UTC) - timedelta(seconds=10),
                )
                session.add(lot)
                await session.commit()
                await session.refresh(lot)
                lot_id_holder.append(lot.id)

        asyncio.run(_setup())
        lot_id = lot_id_holder[0]

        with (
            TestClient(app) as test_client,
            test_client.websocket_connect("/api/v1/ws") as websocket,
        ):
            result = process_auction_ticks()
            assert result["expired_processed"] == 1
            assert result["ticks_processed"] == 0

            raw_data = websocket.receive_text()
            parsed = json.loads(raw_data)
            assert parsed["event"] == "LOT_EXPIRED"
            assert parsed["lot_id"] == str(lot_id)
            assert Decimal(str(parsed["floor_price"])) == Decimal("20000.00")

            take_res = test_client.post(
                f"/api/v1/lots/{lot_id}/take",
                json={"buyer_contact": "too.late@buyer.com"},
            )
            assert take_res.status_code == 409
            assert take_res.json()["detail"] == "Цю річ уже забрав інший покупець"

        async def _verify() -> None:
            async with db_session_factory() as session:
                db_lot = await session.get(Lot, lot_id)
                assert db_lot is not None
                assert db_lot.status == LotStatus.EXPIRED

        asyncio.run(_verify())

    finally:
        app.dependency_overrides.clear()


def test_e2e_accountless_lookup_not_found_and_masked_rejection(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_db

    try:
        with TestClient(app) as client:
            non_existent = client.get("/api/v1/orders/lookup?code=V-2026-9999-9999-9999")
            assert non_existent.status_code == 404
            assert non_existent.json()["detail"] == "Замовлення за вказаним чек-кодом не знайдено"

            masked = client.get("/api/v1/orders/lookup?code=V-2026-ABCD-****-****")
            assert masked.status_code == 404
            assert masked.json()["detail"] == "Замовлення за вказаним чек-кодом не знайдено"

            empty_code = client.get("/api/v1/orders/lookup?code=   ")
            assert empty_code.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_e2e_order_lookup_with_cyrillic_homoglyphs(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_db

    try:
        lot_id_holder: list[uuid.UUID] = []

        async def _setup() -> None:
            async with db_session_factory() as session:
                lot = Lot(
                    title="Raf Simons AW03 Closer Parka",
                    brand="Raf Simons",
                    designer="Raf Simons",
                    season="AW",
                    year=2003,
                    category=LotCategory.OUTERWEAR,
                    subcategory="Parka",
                    tagged_size="48",
                    fits_like="48",
                    measurements={"pit_to_pit": 62, "length": 90},
                    materials={"outer": "Cotton Gabardine"},
                    condition_rating=10,
                    condition_details="Peter Saville Joy Division artwork",
                    country_of_origin="Belgium",
                    start_price=Decimal("150000.00"),
                    floor_price=Decimal("80000.00"),
                    current_price=Decimal("120000.00"),
                    step_amount=Decimal("5000.00"),
                    interval_seconds=60,
                    status=LotStatus.ACTIVE,
                )
                session.add(lot)
                await session.commit()
                await session.refresh(lot)
                lot_id_holder.append(lot.id)

        asyncio.run(_setup())
        lot_id = lot_id_holder[0]

        with TestClient(app) as client:
            take_res = client.post(
                f"/api/v1/lots/{lot_id}/take",
                json={
                    "buyer_contact": "peter.saville@manchester.uk",
                    "shipping_address": {
                        "recipient_name": "Peter Saville",
                        "city": "Manchester",
                        "address": "Factory Road 1",
                    },
                },
            )
            assert take_res.status_code == 200
            real_code = take_res.json()["claim_code"]

            raw_tail = real_code[2:].replace("-", "—")
            cyrillic_tail = (
                raw_tail.replace("A", "А")
                .replace("B", "В")
                .replace("C", "С")
                .replace("E", "Е")
                .replace("H", "Н")
                .replace("O", "О")
                .replace("P", "Р")
                .replace("T", "Т")
                .replace("X", "Х")
            )
            ukr_code_input = f" В—{cyrillic_tail} "

            lookup_res = client.get(f"/api/v1/orders/lookup?code={ukr_code_input}")
            assert lookup_res.status_code == 200
            assert lookup_res.json()["claim_code"] == real_code
            assert lookup_res.json()["lot"]["title"] == "Raf Simons AW03 Closer Parka"

    finally:
        app.dependency_overrides.clear()
