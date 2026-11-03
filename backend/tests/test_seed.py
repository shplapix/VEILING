from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.s3 import s3_service
from app.models.enums import LotCategory, LotStatus, UserRole
from app.models.lot import Lot
from app.models.lot_image import LotImage
from app.models.user import User
from app.scripts.image_generator import generate_png_image
from app.scripts.seed import parse_args, seed_archive_lots, seed_users
from app.scripts.seed_data import ARCHIVE_EXHIBITS
from tests.conftest import FakeS3Service


async def test_seed_archive_lots_success_and_structure(
    db_session: AsyncSession,
) -> None:
    seeded = await seed_archive_lots(db_session, s3=None, skip_s3=True)
    assert len(seeded) == len(ARCHIVE_EXHIBITS)
    assert len(seeded) == 6

    titles = {lot.title for lot in seeded}
    assert 'Бомбер Raf Simons AW01 "Riot! Riot! Riot!" Camo Bomber' in titles
    assert "Мотокуртка Helmut Lang AW99 Astro Biker Jacket" in titles
    assert "Джинси Maison Martin Margiela Artisanal Painted Denim 1990s" in titles
    assert 'Джинси Undercover 85 Denim AW05 "Arts & Crafts"' in titles
    assert 'Шкіряний бомбер Rick Owens AW14 "Moody" Exploder' in titles
    assert 'В\'язаний светр Yohji Yamamoto Pour Homme AW02 "Dandies"' in titles

    raf = next(
        lot
        for lot in seeded
        if lot.title == 'Бомбер Raf Simons AW01 "Riot! Riot! Riot!" Camo Bomber'
    )
    assert raf.brand == "Raf Simons"
    assert raf.designer == "Raf Simons"
    assert raf.year == 2001
    assert raf.season == "Autumn/Winter"
    assert raf.category == LotCategory.OUTERWEAR
    assert raf.subcategory == "Військовий бомбер"
    assert raf.tagged_size == "50"
    assert raf.fits_like == "Oversized L"
    assert raf.condition_rating == 9
    assert raf.status == LotStatus.ACTIVE
    assert raf.current_price == Decimal("180000.00")
    assert raf.floor_price == Decimal("120000.00")
    assert raf.step_amount == Decimal("1500.00")
    assert raf.interval_seconds == 60
    assert len(raf.images) == 5

    margiela = next(
        lot
        for lot in seeded
        if lot.title == "Джинси Maison Martin Margiela Artisanal Painted Denim 1990s"
    )
    assert margiela.brand == "Maison Margiela"
    assert margiela.designer == "Martin Margiela"
    assert margiela.category == LotCategory.BOTTOMS
    assert margiela.condition_rating == 8
    assert len(margiela.images) == 4


async def test_seed_idempotency_without_duplicates(
    db_session: AsyncSession,
) -> None:
    first_run = await seed_archive_lots(db_session, s3=None, skip_s3=True)
    assert len(first_run) == 6

    total_lots_stmt = select(func.count(Lot.id))
    total_images_stmt = select(func.count(LotImage.id))

    lots_count_first = (await db_session.execute(total_lots_stmt)).scalar_one()
    images_count_first = (await db_session.execute(total_images_stmt)).scalar_one()

    assert lots_count_first == 6
    assert images_count_first > 0

    second_run = await seed_archive_lots(db_session, s3=None, skip_s3=True)
    assert len(second_run) == 6

    lots_count_second = (await db_session.execute(total_lots_stmt)).scalar_one()
    images_count_second = (await db_session.execute(total_images_stmt)).scalar_one()

    assert lots_count_second == lots_count_first
    assert images_count_second == images_count_first


async def test_seed_users_idempotency(
    db_session: AsyncSession,
) -> None:
    admin_1, seller_1 = await seed_users(db_session)
    assert admin_1.role == UserRole.ADMIN
    assert admin_1.email == settings.ADMIN_EMAIL
    assert seller_1.role == UserRole.SELLER
    assert seller_1.email == "seller@veiling.test"

    admin_2, seller_2 = await seed_users(db_session)
    assert admin_2.id == admin_1.id
    assert seller_2.id == seller_1.id

    users_count = (await db_session.execute(select(func.count(User.id)))).scalar_one()
    assert users_count == 2


async def test_seed_measurements_and_materials_accuracy(
    db_session: AsyncSession,
) -> None:
    seeded = await seed_archive_lots(db_session, s3=None, skip_s3=True)

    for lot in seeded:
        assert isinstance(lot.measurements, dict)
        assert len(lot.measurements) >= 4
        for k, val in lot.measurements.items():
            assert isinstance(val, int | float)
            assert val > 0, f"Measurement {k} in {lot.title} must be positive"

        assert isinstance(lot.materials, dict)
        assert len(lot.materials) >= 2
        for _mat_key, mat_desc in lot.materials.items():
            assert isinstance(mat_desc, str)
            assert len(mat_desc) > 5

    outerwear_lots = [lot for lot in seeded if lot.category == LotCategory.OUTERWEAR]
    for lot in outerwear_lots:
        assert "pit_to_pit" in lot.measurements
        assert "length" in lot.measurements
        assert "shoulders" in lot.measurements
        assert "sleeve" in lot.measurements

    bottoms_lots = [lot for lot in seeded if lot.category == LotCategory.BOTTOMS]
    for lot in bottoms_lots:
        assert "waist" in lot.measurements
        assert "length" in lot.measurements
        assert "inseam" in lot.measurements
        assert "hem" in lot.measurements


async def test_seed_pricing_and_curatorial_provenance(
    db_session: AsyncSession,
) -> None:
    seeded = await seed_archive_lots(db_session, s3=None, skip_s3=True)

    for lot in seeded:
        assert lot.start_price >= lot.floor_price > Decimal("0.00")
        assert lot.step_amount > Decimal("0.00")
        assert lot.current_price == lot.start_price
        assert lot.interval_seconds == 60
        assert 1 <= lot.condition_rating <= 10
        assert lot.started_at is not None
        assert lot.next_drop_at is not None
        assert lot.next_drop_at > lot.started_at

        assert len(lot.condition_details) > 30
        assert len(lot.provenance_notes or "") > 30
        assert lot.seller_location != ""
        assert "доставка" in lot.shipping_notes.lower()
        assert "кур'" in lot.shipping_notes.lower()


async def test_seed_with_s3_upload_pipeline(
    db_session: AsyncSession,
    fake_s3: FakeS3Service,
) -> None:
    seeded = await seed_archive_lots(db_session, s3=fake_s3, skip_s3=False)
    assert len(seeded) == 6

    total_images = sum(len(lot.images) for lot in seeded)
    assert len(fake_s3.storage) == total_images

    for lot in seeded:
        assert len(lot.images) >= 3
        orders = [img.sort_order for img in lot.images]
        assert orders == sorted(orders)
        assert orders[0] == 0

        for img in lot.images:
            assert img.image_url.startswith("http://localhost:9000/archive-lots/lots/")
            assert img.caption is not None and len(img.caption) > 0


async def test_image_generator_magic_bytes_and_patterns() -> None:
    patterns = [
        "camo",
        "metallic",
        "painted",
        "distressed",
        "leather",
        "knit",
        "hardware",
        "straps",
        "tag",
        "plain",
    ]

    for p in patterns:
        img_bytes = generate_png_image(
            width=200,
            height=200,
            primary_color=(50, 60, 70),
            secondary_color=(20, 25, 30),
            pattern_type=p,
        )
        assert img_bytes.startswith(b"\x89PNG\r\n\x1a\n")
        assert len(img_bytes) > 64

        validated_ext = s3_service.validate_image(img_bytes, "image/png")
        assert validated_ext == ".png"


async def test_seed_reset_flag_functionality(
    db_session: AsyncSession,
) -> None:
    await seed_archive_lots(db_session, s3=None, skip_s3=True)
    first_lots = (await db_session.execute(select(Lot))).scalars().all()
    first_ids = {lot.id for lot in first_lots}
    assert len(first_ids) == 6

    await seed_archive_lots(db_session, s3=None, skip_s3=True, reset=True)
    reset_lots = (await db_session.execute(select(Lot))).scalars().all()
    reset_ids = {lot.id for lot in reset_lots}
    assert len(reset_ids) == 6
    assert reset_ids != first_ids


def test_seed_cli_parser_options() -> None:
    args = parse_args(["--reset", "--skip-s3", "--skip-images", "--quiet"])
    assert args.reset is True
    assert args.skip_s3 is True
    assert args.skip_images is True
    assert args.quiet is True

    default_args = parse_args([])
    assert default_args.reset is False
    assert default_args.skip_s3 is False
    assert default_args.skip_images is False
    assert default_args.quiet is False
