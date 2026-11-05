import argparse
import asyncio
import contextlib
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Protocol

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import Base
from app.core.s3 import s3_service
from app.core.security import get_password_hash
from app.models.enums import UserRole
from app.models.lot import Lot
from app.models.lot_image import LotImage
from app.models.order import Order
from app.models.price_tick import PriceTick
from app.models.user import User
from app.scripts.image_generator import generate_png_image
from app.scripts.seed_data import ARCHIVE_EXHIBITS

PUBLIC_LOTS_DIR = Path("frontend/public/lots")


class S3ClientProtocol(Protocol):
    def validate_image(self, file_data: bytes, content_type: str) -> str: ...

    async def ensure_bucket_exists(self) -> None: ...

    async def upload_image(
        self,
        file_data: bytes,
        content_type: str,
        prefix: str | None = None,
    ) -> tuple[str, str]: ...


async def seed_users(session: AsyncSession) -> tuple[User, User]:
    admin_query = select(User).where(User.email == settings.ADMIN_EMAIL)
    res_admin = await session.execute(admin_query)
    admin_user = res_admin.scalar_one_or_none()

    if admin_user is None:
        admin_user = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            full_name="Veiling Curator Admin",
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(admin_user)
    else:
        admin_user.role = UserRole.ADMIN
        admin_user.is_active = True

    seller_email = "seller@veiling.com"
    seller_query = select(User).where(User.email == seller_email)
    res_seller = await session.execute(seller_query)
    seller_user = res_seller.scalar_one_or_none()

    if seller_user is None:
        seller_user = User(
            email=seller_email,
            hashed_password=get_password_hash("VeilingSeller2026!"),
            full_name="Amsterdam Archive Vault",
            role=UserRole.SELLER,
            is_active=True,
        )
        session.add(seller_user)
    else:
        seller_user.role = UserRole.SELLER
        seller_user.is_active = True

    await session.commit()
    refreshed_admin = (
        await session.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
    ).scalar_one()
    refreshed_seller = (
        await session.execute(select(User).where(User.email == seller_email))
    ).scalar_one()
    return refreshed_admin, refreshed_seller


async def _upload_or_fallback_image(
    s3: S3ClientProtocol | None,
    image_bytes: bytes,
    filename: str,
    skip_s3: bool,
    s3_active: bool = True,
) -> str:
    content_type = "image/jpeg" if filename.lower().endswith((".jpg", ".jpeg")) else "image/png"
    if s3 is not None:
        with contextlib.suppress(Exception):
            s3.validate_image(image_bytes, content_type)
        if not skip_s3 and s3_active:
            with contextlib.suppress(Exception):
                _, url = await s3.upload_image(
                    file_data=image_bytes,
                    content_type=content_type,
                    prefix="lots",
                )
                return url
    elif filename.lower().endswith(".png") and not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG magic bytes")

    clean_base = settings.MINIO_PUBLIC_URL.rstrip("/")
    return f"{clean_base}/lots/{filename}"


async def seed_archive_lots(
    session: AsyncSession,
    s3: S3ClientProtocol | None = None,
    *,
    skip_images: bool = False,
    skip_s3: bool = False,
    reset: bool = False,
) -> list[Lot]:
    if reset:
        await session.execute(delete(Order))
        await session.execute(delete(PriceTick))
        await session.execute(delete(LotImage))
        await session.execute(delete(Lot))
        await session.commit()

    s3_active = False
    if s3 is not None and not skip_s3:
        try:
            await s3.ensure_bucket_exists()
            s3_active = True
        except Exception:
            s3_active = False

    seeded_lots: list[Lot] = []
    now = datetime.now(UTC)

    for exhibit in ARCHIVE_EXHIBITS:
        query = select(Lot).options(selectinload(Lot.images)).where(Lot.title == exhibit.title)
        existing = (await session.execute(query)).scalar_one_or_none()

        if existing is not None:
            if not skip_images:
                has_jpg = any(img.image_url.endswith(".jpg") for img in existing.images)
                if not has_jpg or not existing.images:
                    existing.images.clear()
                    for img_spec in exhibit.images:
                        file_on_disk = PUBLIC_LOTS_DIR / img_spec.filename
                        if file_on_disk.exists():
                            img_bytes = file_on_disk.read_bytes()
                        else:
                            img_bytes = generate_png_image(
                                width=400,
                                height=400,
                                primary_color=img_spec.primary_color,
                                secondary_color=img_spec.secondary_color,
                                pattern_type=img_spec.pattern_type,
                            )
                        image_url = await _upload_or_fallback_image(
                            s3=s3,
                            image_bytes=img_bytes,
                            filename=img_spec.filename,
                            skip_s3=skip_s3,
                            s3_active=s3_active,
                        )
                        new_img = LotImage(
                            image_url=image_url,
                            sort_order=img_spec.sort_order,
                            caption=img_spec.caption,
                        )
                        existing.images.append(new_img)
                    await session.commit()
                seeded_lots.append(existing)
            else:
                seeded_lots.append(existing)
            continue

        started_at = now
        next_drop_at = now + timedelta(seconds=exhibit.interval_seconds)

        lot = Lot(
            title=exhibit.title,
            brand=exhibit.brand,
            designer=exhibit.designer,
            season=exhibit.season,
            year=exhibit.year,
            collection_name=exhibit.collection_name,
            category=exhibit.category,
            subcategory=exhibit.subcategory,
            tagged_size=exhibit.tagged_size,
            fits_like=exhibit.fits_like,
            measurements=exhibit.measurements,
            materials=exhibit.materials,
            condition_rating=exhibit.condition_rating,
            condition_details=exhibit.condition_details,
            country_of_origin=exhibit.country_of_origin,
            provenance_notes=exhibit.provenance_notes,
            seller_location=exhibit.seller_location,
            shipping_notes=exhibit.shipping_notes,
            start_price=exhibit.start_price,
            floor_price=exhibit.floor_price,
            current_price=exhibit.start_price,
            step_amount=exhibit.step_amount,
            interval_seconds=exhibit.interval_seconds,
            status=exhibit.status,
            started_at=started_at,
            next_drop_at=next_drop_at,
        )

        if not skip_images:
            for img_spec in exhibit.images:
                file_on_disk = PUBLIC_LOTS_DIR / img_spec.filename
                if file_on_disk.exists():
                    img_bytes = file_on_disk.read_bytes()
                else:
                    img_bytes = generate_png_image(
                        width=400,
                        height=400,
                        primary_color=img_spec.primary_color,
                        secondary_color=img_spec.secondary_color,
                        pattern_type=img_spec.pattern_type,
                    )
                image_url = await _upload_or_fallback_image(
                    s3=s3,
                    image_bytes=img_bytes,
                    filename=img_spec.filename,
                    skip_s3=skip_s3,
                    s3_active=s3_active,
                )
                lot_image = LotImage(
                    image_url=image_url,
                    sort_order=img_spec.sort_order,
                    caption=img_spec.caption,
                )
                lot.images.append(lot_image)

        session.add(lot)
        await session.commit()

        refreshed = (
            await session.execute(
                select(Lot).options(selectinload(Lot.images)).where(Lot.id == lot.id)
            )
        ).scalar_one()
        seeded_lots.append(refreshed)

    return seeded_lots


async def run_seed(
    db_url: str | None = None,
    skip_s3: bool = False,
    skip_images: bool = False,
    reset: bool = False,
    verbose: bool = True,
) -> list[Lot]:
    target_url = db_url or settings.DATABASE_URL
    engine = create_async_engine(
        target_url,
        echo=False,
        pool_pre_ping=True,
    )
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        async with async_session() as session:
            admin_user, seller_user = await seed_users(session)
            if verbose:
                sys.stdout.write(
                    f"Users ready: admin={admin_user.email}, seller={seller_user.email}\n"
                )

            lots = await seed_archive_lots(
                session=session,
                s3=s3_service,
                skip_images=skip_images,
                skip_s3=skip_s3,
                reset=reset,
            )
            if verbose:
                sys.stdout.write(f"Successfully seeded {len(lots)} archive lots\n")
            return lots
    finally:
        await engine.dispose()


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed VEILING database with iconic archive fashion exhibits"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Purge existing lots before seeding",
    )
    parser.add_argument(
        "--skip-s3",
        action="store_true",
        help="Skip live S3 upload and use static MinIO public URLs",
    )
    parser.add_argument(
        "--skip-images",
        action="store_true",
        help="Do not attach images to seeded lots",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Custom database connection URL",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational stdout output",
    )
    return parser.parse_args(args)


def main() -> None:
    parsed = parse_args()
    try:
        asyncio.run(
            run_seed(
                db_url=parsed.db_url,
                skip_s3=parsed.skip_s3,
                skip_images=parsed.skip_images,
                reset=parsed.reset,
                verbose=not parsed.quiet,
            )
        )
    except Exception as exc:
        sys.stderr.write(f"Seed error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
