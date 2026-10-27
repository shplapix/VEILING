import re
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import LotCategory, LotStatus, OrderStatus, UserRole
from app.models.lot import Lot
from app.models.lot_image import LotImage
from app.models.order import Order, generate_claim_code
from app.models.price_tick import PriceTick
from app.models.user import User


def test_generate_claim_code_format() -> None:
    code = generate_claim_code()
    pattern = r"^V-\d{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}$"
    assert re.match(pattern, code) is not None
    code2 = generate_claim_code()
    assert code != code2


async def test_create_user(db_session: AsyncSession) -> None:
    user = User(
        email="archive_curator@veiling.com",
        hashed_password="hashed_pass_value",
        full_name="Archive Curator",
        role=UserRole.SELLER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert isinstance(user.id, uuid.UUID)
    assert user.email == "archive_curator@veiling.com"
    assert user.role == UserRole.SELLER
    assert user.is_active is True
    assert user.created_at is not None
    assert user.updated_at is not None


async def test_user_email_unique_constraint(db_session: AsyncSession) -> None:
    user1 = User(
        email="duplicate@veiling.com",
        hashed_password="pass1",
        full_name="User One",
    )
    user2 = User(
        email="duplicate@veiling.com",
        hashed_password="pass2",
        full_name="User Two",
    )
    db_session.add(user1)
    await db_session.commit()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


async def test_create_lot_with_json_and_images(db_session: AsyncSession) -> None:
    measurements = {
        "pit_to_pit": 62,
        "length": 71,
        "shoulders": 54,
        "sleeve": 66,
    }
    materials = {
        "outer": "100% Cotton",
        "lining": "100% Cupro",
        "hardware": "Raccagni",
    }
    lot = Lot(
        title="Raf Simons AW01 Riot Bomber",
        brand="Raf Simons",
        designer="Raf Simons",
        season="Autumn/Winter",
        year=2001,
        collection_name="Riot! Riot! Riot!",
        category=LotCategory.OUTERWEAR,
        subcategory="Bomber",
        tagged_size="50",
        fits_like="Oversized L",
        measurements=measurements,
        materials=materials,
        condition_rating=9,
        condition_details="Archival condition with authentic vintage patina",
        country_of_origin="Belgium",
        provenance_notes="Runway piece, private Antwerp collection",
        start_price=Decimal("180000.00"),
        floor_price=Decimal("90000.00"),
        current_price=Decimal("180000.00"),
        step_amount=Decimal("2500.00"),
        interval_seconds=60,
        status=LotStatus.ACTIVE,
    )
    db_session.add(lot)
    await db_session.commit()
    await db_session.refresh(lot)

    assert lot.measurements["pit_to_pit"] == 62
    assert lot.materials["hardware"] == "Raccagni"
    assert lot.seller_location == "Амстердам, Нідерланди"

    img1 = LotImage(
        lot_id=lot.id,
        image_url="http://localhost:9000/archive-lots/front.jpg",
        sort_order=0,
        caption="Front view",
    )
    img2 = LotImage(
        lot_id=lot.id,
        image_url="http://localhost:9000/archive-lots/tag.jpg",
        sort_order=1,
        caption="Season tag",
    )
    db_session.add_all([img1, img2])
    await db_session.commit()

    query = select(Lot).where(Lot.id == lot.id)
    result = await db_session.execute(query)
    fetched_lot = result.scalar_one()

    await db_session.refresh(fetched_lot, ["images"])
    assert len(fetched_lot.images) == 2
    assert fetched_lot.images[0].sort_order == 0
    assert fetched_lot.images[1].sort_order == 1


async def test_lot_image_cascade_delete(db_session: AsyncSession) -> None:
    lot = Lot(
        title="Helmut Lang AW99 Astro Jacket",
        brand="Helmut Lang",
        designer="Helmut Lang",
        season="Autumn/Winter",
        year=1999,
        category=LotCategory.OUTERWEAR,
        subcategory="Jacket",
        tagged_size="48",
        fits_like="Slim M",
        measurements={"pit_to_pit": 52, "length": 68},
        materials={"outer": "Bonded Cotton"},
        condition_rating=8,
        condition_details="Slight collar aging",
        country_of_origin="Italy",
        start_price=Decimal("95000.00"),
        floor_price=Decimal("50000.00"),
        current_price=Decimal("95000.00"),
        step_amount=Decimal("1500.00"),
        interval_seconds=60,
        status=LotStatus.ACTIVE,
    )
    db_session.add(lot)
    await db_session.commit()

    img = LotImage(
        lot_id=lot.id,
        image_url="http://localhost:9000/archive-lots/astro.jpg",
        sort_order=0,
    )
    db_session.add(img)
    await db_session.commit()

    await db_session.delete(lot)
    await db_session.commit()

    img_query = select(LotImage).where(LotImage.lot_id == lot.id)
    img_res = await db_session.execute(img_query)
    assert img_res.scalar_one_or_none() is None


async def test_price_ticks_recording(db_session: AsyncSession) -> None:
    lot = Lot(
        title="Maison Martin Margiela Artisanal Vest",
        brand="Maison Martin Margiela",
        designer="Martin Margiela",
        season="Spring/Summer",
        year=2000,
        category=LotCategory.TOPS,
        subcategory="Vest",
        tagged_size="M",
        fits_like="True M",
        measurements={"pit_to_pit": 50, "length": 60},
        materials={"outer": "Reconstructed Leather"},
        condition_rating=10,
        condition_details="Pristine archive condition",
        country_of_origin="France",
        start_price=Decimal("120000.00"),
        floor_price=Decimal("70000.00"),
        current_price=Decimal("120000.00"),
        step_amount=Decimal("2000.00"),
        status=LotStatus.ACTIVE,
    )
    db_session.add(lot)
    await db_session.commit()

    tick = PriceTick(
        lot_id=lot.id,
        price=Decimal("118000.00"),
    )
    db_session.add(tick)
    await db_session.commit()

    query = select(PriceTick).where(PriceTick.lot_id == lot.id)
    result = await db_session.execute(query)
    ticks = result.scalars().all()
    assert len(ticks) == 1
    assert ticks[0].price == Decimal("118000.00")


async def test_order_creation_and_single_order_per_lot_constraint(
    db_session: AsyncSession,
) -> None:
    lot = Lot(
        title="Undercover AW02 Witch's Cell Division Jacket",
        brand="Undercover",
        designer="Jun Takahashi",
        season="Autumn/Winter",
        year=2002,
        category=LotCategory.OUTERWEAR,
        subcategory="Jacket",
        tagged_size="L",
        fits_like="Relaxed L",
        measurements={"pit_to_pit": 58, "length": 70},
        materials={"outer": "Nylon blend"},
        condition_rating=9,
        condition_details="Excellent archive condition",
        country_of_origin="Japan",
        start_price=Decimal("80000.00"),
        floor_price=Decimal("45000.00"),
        current_price=Decimal("65000.00"),
        step_amount=Decimal("1000.00"),
        status=LotStatus.TAKEN,
    )
    db_session.add(lot)
    await db_session.commit()

    order1 = Order(
        lot_id=lot.id,
        claim_code=generate_claim_code(),
        final_price=Decimal("65000.00"),
        savings_from_ceiling=Decimal("15000.00"),
        savings_percentage=19,
        status=OrderStatus.PAID,
        buyer_contact="collector@kyiv.ua",
        shipping_address={
            "recipient": "Taras Shevchenko",
            "city": "Kyiv",
            "country": "Ukraine",
            "postal_code": "01001",
            "address_line": "Khreshchatyk 1",
        },
        payment_reference="pay_ref_test_12345",
    )
    db_session.add(order1)
    await db_session.commit()
    await db_session.refresh(order1)

    assert order1.id is not None
    assert order1.status == OrderStatus.PAID
    assert order1.savings_percentage == 19

    order2 = Order(
        lot_id=lot.id,
        claim_code=generate_claim_code(),
        final_price=Decimal("65000.00"),
        savings_from_ceiling=Decimal("15000.00"),
        savings_percentage=19,
        status=OrderStatus.PAID,
        buyer_contact="other@kyiv.ua",
        shipping_address={"city": "Lviv"},
        payment_reference="pay_ref_test_99999",
    )
    db_session.add(order2)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


async def test_lot_condition_rating_bounds(db_session: AsyncSession) -> None:
    lot_invalid_low = Lot(
        title="Invalid Rating Low",
        brand="Raf Simons",
        designer="Raf Simons",
        season="AW01",
        year=2001,
        category=LotCategory.OUTERWEAR,
        subcategory="Bomber",
        tagged_size="50",
        fits_like="L",
        measurements={},
        materials={},
        condition_rating=0,
        condition_details="Invalid rating 0",
        country_of_origin="Belgium",
        start_price=Decimal("100000.00"),
        floor_price=Decimal("50000.00"),
        current_price=Decimal("100000.00"),
        step_amount=Decimal("1000.00"),
    )
    db_session.add(lot_invalid_low)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    lot_invalid_high = Lot(
        title="Invalid Rating High",
        brand="Raf Simons",
        designer="Raf Simons",
        season="AW01",
        year=2001,
        category=LotCategory.OUTERWEAR,
        subcategory="Bomber",
        tagged_size="50",
        fits_like="L",
        measurements={},
        materials={},
        condition_rating=11,
        condition_details="Invalid rating 11",
        country_of_origin="Belgium",
        start_price=Decimal("100000.00"),
        floor_price=Decimal("50000.00"),
        current_price=Decimal("100000.00"),
        step_amount=Decimal("1000.00"),
    )
    db_session.add(lot_invalid_high)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


async def test_lot_pricing_constraints(db_session: AsyncSession) -> None:
    inverted_lot = Lot(
        title="Inverted Prices",
        brand="Helmut Lang",
        designer="Helmut Lang",
        season="AW99",
        year=1999,
        category=LotCategory.OUTERWEAR,
        subcategory="Parka",
        tagged_size="48",
        fits_like="M",
        measurements={},
        materials={},
        condition_rating=8,
        condition_details="Vintage",
        country_of_origin="Italy",
        start_price=Decimal("50000.00"),
        floor_price=Decimal("80000.00"),
        current_price=Decimal("50000.00"),
        step_amount=Decimal("1000.00"),
    )
    db_session.add(inverted_lot)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    zero_step_lot = Lot(
        title="Zero Step",
        brand="Helmut Lang",
        designer="Helmut Lang",
        season="AW99",
        year=1999,
        category=LotCategory.OUTERWEAR,
        subcategory="Parka",
        tagged_size="48",
        fits_like="M",
        measurements={},
        materials={},
        condition_rating=8,
        condition_details="Vintage",
        country_of_origin="Italy",
        start_price=Decimal("80000.00"),
        floor_price=Decimal("50000.00"),
        current_price=Decimal("80000.00"),
        step_amount=Decimal("0.00"),
    )
    db_session.add(zero_step_lot)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


async def test_lot_image_invalid_foreign_key_rejected(
    db_session: AsyncSession,
) -> None:
    img = LotImage(
        lot_id=uuid.uuid4(),
        image_url="http://localhost:9000/archive-lots/orphan.jpg",
    )
    db_session.add(img)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


async def test_price_ticks_cascade_delete(db_session: AsyncSession) -> None:
    lot = Lot(
        title="Margiela Artisanal Vest",
        brand="Maison Martin Margiela",
        designer="Martin Margiela",
        season="SS00",
        year=2000,
        category=LotCategory.TOPS,
        subcategory="Vest",
        tagged_size="M",
        fits_like="M",
        measurements={},
        materials={},
        condition_rating=9,
        condition_details="Pristine",
        country_of_origin="France",
        start_price=Decimal("100000.00"),
        floor_price=Decimal("60000.00"),
        current_price=Decimal("100000.00"),
        step_amount=Decimal("2000.00"),
        status=LotStatus.ACTIVE,
    )
    db_session.add(lot)
    await db_session.commit()

    lot_id = lot.id
    tick = PriceTick(lot_id=lot_id, price=Decimal("98000.00"))
    db_session.add(tick)
    await db_session.commit()

    await db_session.delete(lot)
    await db_session.commit()

    res = await db_session.execute(select(PriceTick).where(PriceTick.lot_id == lot_id))
    assert len(res.scalars().all()) == 0


async def test_order_claim_code_unique_constraint(
    db_session: AsyncSession,
) -> None:
    lot1 = Lot(
        title="Lot One",
        brand="Undercover",
        designer="Jun Takahashi",
        season="AW02",
        year=2002,
        category=LotCategory.OUTERWEAR,
        subcategory="Jacket",
        tagged_size="L",
        fits_like="L",
        measurements={},
        materials={},
        condition_rating=8,
        condition_details="Good",
        country_of_origin="Japan",
        start_price=Decimal("60000.00"),
        floor_price=Decimal("30000.00"),
        current_price=Decimal("45000.00"),
        step_amount=Decimal("1000.00"),
    )
    lot2 = Lot(
        title="Lot Two",
        brand="Undercover",
        designer="Jun Takahashi",
        season="AW02",
        year=2002,
        category=LotCategory.OUTERWEAR,
        subcategory="Jacket",
        tagged_size="L",
        fits_like="L",
        measurements={},
        materials={},
        condition_rating=8,
        condition_details="Good",
        country_of_origin="Japan",
        start_price=Decimal("60000.00"),
        floor_price=Decimal("30000.00"),
        current_price=Decimal("45000.00"),
        step_amount=Decimal("1000.00"),
    )
    db_session.add_all([lot1, lot2])
    await db_session.commit()

    shared_claim_code = generate_claim_code()
    order1 = Order(
        lot_id=lot1.id,
        claim_code=shared_claim_code,
        final_price=Decimal("45000.00"),
        savings_from_ceiling=Decimal("15000.00"),
        savings_percentage=25,
        status=OrderStatus.PAID,
        buyer_contact="first@veiling.com",
        shipping_address={"city": "Kyiv"},
        payment_reference="ref1",
    )
    order2 = Order(
        lot_id=lot2.id,
        claim_code=shared_claim_code,
        final_price=Decimal("45000.00"),
        savings_from_ceiling=Decimal("15000.00"),
        savings_percentage=25,
        status=OrderStatus.PAID,
        buyer_contact="second@veiling.com",
        shipping_address={"city": "Lviv"},
        payment_reference="ref2",
    )
    db_session.add(order1)
    await db_session.commit()

    db_session.add(order2)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()
