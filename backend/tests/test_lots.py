import uuid
from decimal import Decimal
from unittest.mock import patch

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.models.enums import LotCategory, LotStatus, UserRole
from app.models.user import User
from tests.conftest import FakeS3Service


async def create_user_with_role(
    db_session: AsyncSession,
    email: str,
    role: UserRole,
) -> tuple[User, str]:
    user = User(
        email=email,
        hashed_password=get_password_hash("StrongSecret2026!"),
        role=role,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return user, token


def valid_lot_payload() -> dict[str, object]:
    return {
        "title": "Raf Simons Riot Bomber AW01",
        "brand": "Raf Simons",
        "designer": "Raf Simons",
        "season": "Autumn/Winter 2001",
        "year": 2001,
        "collection_name": "Riot! Riot! Riot!",
        "category": LotCategory.OUTERWEAR.value,
        "subcategory": "Bomber Jacket",
        "tagged_size": "50",
        "fits_like": "Oversized L",
        "measurements": {
            "pit_to_pit": 62,
            "length": 71,
            "shoulders": 54,
            "sleeve": 66,
        },
        "materials": {
            "outer": "100% Cotton Camo Gabardine",
            "lining": "100% Cupro",
        },
        "condition_rating": 9,
        "condition_details": "Archival preservation, natural vintage patina",
        "country_of_origin": "Belgium",
        "provenance_notes": "Private collection, Antwerp",
        "seller_location": "Antwerp, Belgium",
        "shipping_notes": "Insured courier express across Europe",
        "start_price": "180000.00",
        "floor_price": "90000.00",
        "step_amount": "2500.00",
        "interval_seconds": 60,
        "status": LotStatus.ACTIVE.value,
        "images": [
            {
                "image_url": "http://localhost:9000/archive-lots/raf1.jpg",
                "display_order": 0,
                "caption": "Front silhouette",
            },
            {
                "image_url": "http://localhost:9000/archive-lots/raf2.jpg",
                "display_order": 1,
                "caption": "Archival patch detail",
            },
        ],
    }


async def test_create_lot_anonymous_forbidden(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/lots", json=valid_lot_payload())
    assert resp.status_code == 401


async def test_create_lot_buyer_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "buyer@veiling.test",
        UserRole.CUSTOMER,
    )
    resp = await client.post(
        "/api/v1/lots",
        json=valid_lot_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Seller privileges required"


async def test_create_lot_seller_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "seller@veiling.test",
        UserRole.SELLER,
    )
    payload = valid_lot_payload()
    resp = await client.post(
        "/api/v1/lots",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == payload["title"]
    assert data["brand"] == payload["brand"]
    assert data["designer"] == payload["designer"]
    assert data["year"] == 2001
    assert data["condition_rating"] == 9
    assert data["measurements"] == payload["measurements"]
    assert data["materials"] == payload["materials"]
    assert Decimal(data["start_price"]) == Decimal("180000.00")
    assert Decimal(data["floor_price"]) == Decimal("90000.00")
    assert Decimal(data["current_price"]) == Decimal("180000.00")
    assert Decimal(data["step_amount"]) == Decimal("2500.00")
    assert data["interval_seconds"] == 60
    assert data["status"] == LotStatus.ACTIVE.value
    assert data["started_at"] is not None
    assert data["next_drop_at"] is not None
    assert len(data["images"]) == 2
    assert data["images"][0]["display_order"] == 0
    assert data["images"][0]["sort_order"] == 0
    assert data["images"][1]["display_order"] == 1


async def test_create_lot_admin_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "admin@veiling.test",
        UserRole.ADMIN,
    )
    resp = await client.post(
        "/api/v1/lots",
        json=valid_lot_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["brand"] == "Raf Simons"


async def test_create_lot_designer_fallback_to_brand(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "seller_designer@veiling.test",
        UserRole.SELLER,
    )
    payload = valid_lot_payload()
    payload.pop("designer", None)
    resp = await client.post(
        "/api/v1/lots",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["designer"] == "Raf Simons"


async def test_create_lot_price_validation_floor_above_ceiling(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "seller_prices@veiling.test",
        UserRole.SELLER,
    )
    payload = valid_lot_payload()
    payload["start_price"] = "50000.00"
    payload["floor_price"] = "80000.00"
    resp = await client.post(
        "/api/v1/lots",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


async def test_create_lot_zero_or_negative_prices(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "seller_zero@veiling.test",
        UserRole.SELLER,
    )
    payload_zero_start = valid_lot_payload()
    payload_zero_start["start_price"] = "0.00"
    payload_zero_start["floor_price"] = "0.00"
    resp = await client.post(
        "/api/v1/lots",
        json=payload_zero_start,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422

    payload_negative_step = valid_lot_payload()
    payload_negative_step["step_amount"] = "-100.00"
    resp_step = await client.post(
        "/api/v1/lots",
        json=payload_negative_step,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_step.status_code == 422

    payload_zero_interval = valid_lot_payload()
    payload_zero_interval["interval_seconds"] = 0
    resp_interval = await client.post(
        "/api/v1/lots",
        json=payload_zero_interval,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_interval.status_code == 422


async def test_create_lot_condition_rating_boundaries(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "seller_condition@veiling.test",
        UserRole.SELLER,
    )
    payload_low = valid_lot_payload()
    payload_low["condition_rating"] = 0
    resp_low = await client.post(
        "/api/v1/lots",
        json=payload_low,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_low.status_code == 422

    payload_high = valid_lot_payload()
    payload_high["condition_rating"] = 11
    resp_high = await client.post(
        "/api/v1/lots",
        json=payload_high,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_high.status_code == 422


async def test_create_lot_year_boundaries(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "seller_year@veiling.test",
        UserRole.SELLER,
    )
    payload_old = valid_lot_payload()
    payload_old["year"] = 1850
    resp_old = await client.post(
        "/api/v1/lots",
        json=payload_old,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_old.status_code == 422

    payload_future = valid_lot_payload()
    payload_future["year"] = 2150
    resp_future = await client.post(
        "/api/v1/lots",
        json=payload_future,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_future.status_code == 422


async def test_create_lot_missing_required_fields(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "seller_missing@veiling.test",
        UserRole.SELLER,
    )
    payload_no_title = valid_lot_payload()
    payload_no_title.pop("title")
    resp_no_title = await client.post(
        "/api/v1/lots",
        json=payload_no_title,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_no_title.status_code == 422

    payload_no_brand = valid_lot_payload()
    payload_no_brand.pop("brand")
    resp_no_brand = await client.post(
        "/api/v1/lots",
        json=payload_no_brand,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_no_brand.status_code == 422


async def test_upload_image_permissions(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    file_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    files = {"file": ("test.jpg", file_bytes, "image/jpeg")}

    resp_anon = await client.post("/api/v1/lots/upload-image", files=files)
    assert resp_anon.status_code == 401

    _, buyer_token = await create_user_with_role(
        db_session,
        "buyer_img@veiling.test",
        UserRole.CUSTOMER,
    )
    files = {"file": ("test.jpg", file_bytes, "image/jpeg")}
    resp_buyer = await client.post(
        "/api/v1/lots/upload-image",
        files=files,
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert resp_buyer.status_code == 403


async def test_upload_image_mime_and_size_validation(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_s3: FakeS3Service,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "seller_upload@veiling.test",
        UserRole.SELLER,
    )
    headers = {"Authorization": f"Bearer {token}"}

    with patch("app.api.v1.lots.s3_service", fake_s3):
        bad_mime_file = {"file": ("doc.pdf", b"%PDF-1.4", "application/pdf")}
        resp_bad_mime = await client.post(
            "/api/v1/lots/upload-image",
            files=bad_mime_file,
            headers=headers,
        )
        assert resp_bad_mime.status_code == 400
        assert "Invalid image type" in resp_bad_mime.json()["detail"]

        empty_file = {"file": ("empty.jpg", b"", "image/jpeg")}
        resp_empty = await client.post(
            "/api/v1/lots/upload-image",
            files=empty_file,
            headers=headers,
        )
        assert resp_empty.status_code == 400
        assert "empty" in resp_empty.json()["detail"].lower()

        large_bytes = b"X" * (11 * 1024 * 1024)
        large_file = {"file": ("huge.jpg", large_bytes, "image/jpeg")}
        resp_large = await client.post(
            "/api/v1/lots/upload-image",
            files=large_file,
            headers=headers,
        )
        assert resp_large.status_code == 400
        assert "exceeds" in resp_large.json()["detail"].lower()

        good_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"
        good_file = {"file": ("sample.jpg", good_bytes, "image/jpeg")}
        resp_good = await client.post(
            "/api/v1/lots/upload-image",
            files=good_file,
            headers=headers,
        )
        assert resp_good.status_code == 200
        body = resp_good.json()
        assert "image_url" in body
        assert "key" in body
        assert body["image_url"].endswith(".jpg")


async def test_add_image_to_lot_endpoint(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_s3: FakeS3Service,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "seller_lot_img@veiling.test",
        UserRole.SELLER,
    )
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/lots",
        json=valid_lot_payload(),
        headers=headers,
    )
    assert create_resp.status_code == 201
    lot_id = create_resp.json()["id"]

    with patch("app.api.v1.lots.s3_service", fake_s3):
        good_bytes = b"\x89PNG\r\n\x1a\n"
        files = {"file": ("patch.png", good_bytes, "image/png")}
        data = {"display_order": "5", "caption": "Macro fabric texture"}
        img_resp = await client.post(
            f"/api/v1/lots/{lot_id}/images",
            files=files,
            data=data,
            headers=headers,
        )
        assert img_resp.status_code == 201
        img_data = img_resp.json()
        assert img_data["display_order"] == 5
        assert img_data["sort_order"] == 5
        assert img_data["caption"] == "Macro fabric texture"
        assert img_data["image_url"].endswith(".png")

        non_existent_id = uuid.uuid4()
        files_err = {"file": ("patch.png", good_bytes, "image/png")}
        resp_not_found = await client.post(
            f"/api/v1/lots/{non_existent_id}/images",
            files=files_err,
            data={"display_order": "1"},
            headers=headers,
        )
        assert resp_not_found.status_code == 404


async def test_get_and_list_lots_with_images(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    _, token = await create_user_with_role(
        db_session,
        "seller_list@veiling.test",
        UserRole.SELLER,
    )
    create_resp = await client.post(
        "/api/v1/lots",
        json=valid_lot_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_resp.status_code == 201
    lot_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/lots/{lot_id}")
    assert get_resp.status_code == 200
    single = get_resp.json()
    assert single["id"] == lot_id
    assert len(single["images"]) == 2

    list_resp = await client.get("/api/v1/lots?status=ACTIVE")
    assert list_resp.status_code == 200
    lots = list_resp.json()
    assert any(lot["id"] == lot_id for lot in lots)
