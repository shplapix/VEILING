from decimal import Decimal
from typing import Any

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import LotCategory, LotStatus
from app.models.lot import Lot


async def _create_lot_and_order(
    client: AsyncClient,
    db_session: AsyncSession,
    title: str = "Undercover AW02 Witch's Cell Division Jacket",
) -> dict[str, Any]:
    lot = Lot(
        title=title,
        brand="Undercover",
        designer="Jun Takahashi",
        season="AW",
        year=2002,
        category=LotCategory.OUTERWEAR,
        subcategory="Jacket",
        tagged_size="L",
        fits_like="Slim L",
        measurements={"pit_to_pit": 54, "length": 68},
        materials={"outer": "Cotton 100%"},
        condition_rating=9,
        condition_details="Collector archive piece",
        country_of_origin="Japan",
        start_price=Decimal("95000.00"),
        floor_price=Decimal("45000.00"),
        current_price=Decimal("72000.00"),
        step_amount=Decimal("2000.00"),
        interval_seconds=60,
        status=LotStatus.ACTIVE,
    )
    db_session.add(lot)
    await db_session.commit()
    await db_session.refresh(lot)

    take_res = await client.post(
        f"/api/v1/lots/{lot.id}/take",
        json={
            "buyer_contact": "collector@tokyo.archive",
            "shipping_address": {
                "recipient_name": "Kenji Sato",
                "city": "Київ",
                "address": "вул. Хрещатик, 1",
            },
        },
    )
    assert take_res.status_code == 200
    take_data = take_res.json()
    return {
        "lot": lot,
        "claim_code": take_data["claim_code"],
        "order": take_data["order"],
    }


async def test_order_lookup_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    data = await _create_lot_and_order(client, db_session)
    claim_code = data["claim_code"]

    response = await client.get(f"/api/v1/orders/lookup?code={claim_code}")
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["claim_code"] == claim_code
    assert res_data["buyer_contact"] == "collector@tokyo.archive"
    assert res_data["status"] == "PAID"
    assert float(res_data["final_price"]) == 72000.0
    assert res_data["savings_percentage"] == 24
    assert res_data["lot"] is not None
    assert res_data["lot"]["title"] == "Undercover AW02 Witch's Cell Division Jacket"
    assert res_data["lot"]["brand"] == "Undercover"


async def test_order_lookup_case_insensitive_and_whitespace(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    data = await _create_lot_and_order(client, db_session, title="Margiela Artisanal Vest")
    claim_code = data["claim_code"]

    padded_lower_code = f"  {claim_code.lower()}  "
    response = await client.get(f"/api/v1/orders/lookup?code={padded_lower_code}")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["claim_code"] == claim_code
    assert res_data["lot"]["title"] == "Margiela Artisanal Vest"


async def test_order_lookup_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/orders/lookup?code=V-9999-XXXX-YYYY-ZZZZ")
    assert response.status_code == 404
    assert response.json()["detail"] == "Замовлення за вказаним чек-кодом не знайдено"


async def test_order_lookup_homoglyphs_and_dashes(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    data = await _create_lot_and_order(client, db_session, title="Helmut Lang Astro AW99")
    real_code = data["claim_code"]

    raw_tail = real_code[2:].replace("-", "—")
    cyrillic_tail = raw_tail.replace("A", "А").replace("B", "В").replace("C", "С").replace("E", "Е")
    ukr_input = f" В—{cyrillic_tail} "

    response = await client.get(f"/api/v1/orders/lookup?code={ukr_input}")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["claim_code"] == real_code
    assert res_data["lot"]["title"] == "Helmut Lang Astro AW99"


async def test_order_lookup_masked_code_rejected(client: AsyncClient) -> None:
    response = await client.get("/api/v1/orders/lookup?code=V-2026-****-****")
    assert response.status_code == 404


async def test_order_ledger_returns_public_records_without_pii_leak(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    item1 = await _create_lot_and_order(client, db_session, title="Raf Simons Riot Bomber")
    item2 = await _create_lot_and_order(client, db_session, title="Helmut Lang Painter Denim")

    response = await client.get("/api/v1/orders/ledger")
    assert response.status_code == 200
    ledger = response.json()
    assert isinstance(ledger, list)
    assert len(ledger) >= 2

    lot_ids = [record["lot_id"] for record in ledger]
    assert str(item1["lot"].id) in lot_ids
    assert str(item2["lot"].id) in lot_ids

    for record in ledger:
        assert "final_price" in record
        assert "savings_percentage" in record
        assert "lot" in record
        assert "buyer_contact" not in record
        assert "shipping_address" not in record
        assert "payment_reference" not in record
        assert "user_id" not in record
        assert record["claim_code"].endswith("****-****")
        if record["lot"]:
            assert "title" in record["lot"]
            assert "brand" in record["lot"]
