import asyncio
import contextlib
import secrets
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_seller, get_db, get_optional_current_user
from app.core.redis import publish_message
from app.core.s3 import s3_service
from app.models.enums import LotStatus, OrderStatus
from app.models.lot import Lot
from app.models.lot_image import LotImage
from app.models.order import Order, generate_claim_code
from app.models.user import User
from app.schemas.lot import ImageUploadResponse, LotCreate, LotImageRead, LotRead
from app.schemas.order import OrderRead, TakeLotRequest, TakeLotResponse
from app.schemas.ws import LotTakenEvent, serialize_auction_event

router = APIRouter(prefix="/lots", tags=["lots"])


class _RefCountedLock:
    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self.ref_count = 0


_lot_locks: dict[uuid.UUID, _RefCountedLock] = {}
_lot_locks_guard = asyncio.Lock()


@contextlib.asynccontextmanager
async def _acquire_lot_lock(lot_id: uuid.UUID) -> AsyncIterator[None]:
    async with _lot_locks_guard:
        if lot_id not in _lot_locks:
            _lot_locks[lot_id] = _RefCountedLock()
        entry = _lot_locks[lot_id]
        entry.ref_count += 1
    try:
        async with entry.lock:
            yield
    finally:
        async with _lot_locks_guard:
            entry.ref_count -= 1
            if entry.ref_count <= 0 and lot_id in _lot_locks:
                del _lot_locks[lot_id]


@router.post("", response_model=LotRead, status_code=status.HTTP_201_CREATED)
async def create_lot(
    payload: LotCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_seller)],
) -> Lot:
    now = datetime.now(UTC)
    is_active = payload.status == LotStatus.ACTIVE
    started_at = now if is_active else None
    next_drop_at = (now + timedelta(seconds=payload.interval_seconds)) if is_active else None

    lot = Lot(
        title=payload.title,
        brand=payload.brand,
        designer=payload.designer or payload.brand,
        season=payload.season,
        year=payload.year,
        collection_name=payload.collection_name,
        category=payload.category,
        subcategory=payload.subcategory,
        tagged_size=payload.tagged_size,
        fits_like=payload.fits_like,
        measurements=payload.measurements,
        materials=payload.materials,
        condition_rating=payload.condition_rating,
        condition_details=payload.condition_details,
        country_of_origin=payload.country_of_origin,
        provenance_notes=payload.provenance_notes,
        seller_location=payload.seller_location,
        shipping_notes=payload.shipping_notes,
        start_price=payload.start_price,
        floor_price=payload.floor_price,
        current_price=payload.start_price,
        step_amount=payload.step_amount,
        interval_seconds=payload.interval_seconds,
        status=payload.status,
        started_at=started_at,
        next_drop_at=next_drop_at,
    )

    for img in payload.images:
        lot_image = LotImage(
            image_url=img.image_url,
            sort_order=img.sort_order,
            caption=img.caption,
        )
        lot.images.append(lot_image)

    db.add(lot)
    await db.commit()

    query = select(Lot).options(selectinload(Lot.images)).where(Lot.id == lot.id)
    result = await db.execute(query)
    return result.scalar_one()


@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_lot_image(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_seller)],
) -> ImageUploadResponse:
    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content type is missing",
        )
    try:
        s3_service.validate_content_type(file.content_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None

    contents = await file.read()
    try:
        s3_service.validate_image_size(len(contents))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None

    key, url = await s3_service.upload_image(
        file_data=contents,
        content_type=file.content_type,
        prefix="lots",
    )
    return ImageUploadResponse(image_url=url, key=key)


@router.post(
    "/{lot_id}/images",
    response_model=LotImageRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_image_to_lot(
    lot_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_seller)],
    file: Annotated[UploadFile, File(...)],
    sort_order: Annotated[int, Form()] = 0,
    display_order: Annotated[int | None, Form()] = None,
    caption: Annotated[str | None, Form()] = None,
) -> LotImage:
    lot = await db.get(Lot, lot_id)
    if lot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot not found",
        )
    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content type is missing",
        )
    try:
        s3_service.validate_content_type(file.content_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None

    contents = await file.read()
    try:
        s3_service.validate_image_size(len(contents))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None

    effective_order = display_order if display_order is not None else sort_order
    _, url = await s3_service.upload_image(
        file_data=contents,
        content_type=file.content_type,
        prefix=f"lots/{lot_id}",
    )
    image = LotImage(
        lot_id=lot_id,
        image_url=url,
        sort_order=effective_order,
        caption=caption,
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image


@router.post("/{lot_id}/take", response_model=TakeLotResponse)
async def take_lot(
    lot_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    payload: TakeLotRequest | None = None,
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
) -> TakeLotResponse:
    req = payload or TakeLotRequest()
    if req.buyer_contact and req.buyer_contact.strip():
        buyer_contact = req.buyer_contact.strip()
    elif current_user and current_user.email:
        buyer_contact = current_user.email
    else:
        buyer_contact = "guest@veiling.archive"

    payment_ref = (
        req.payment_reference if req.payment_reference else f"PAY-{secrets.token_hex(6).upper()}"
    )
    shipping_addr = (
        req.shipping_address if req.shipping_address else {"delivery": "pending_contact"}
    )

    async with _acquire_lot_lock(lot_id):
        query = select(Lot).where(Lot.id == lot_id).with_for_update()
        result = await db.execute(query)
        lot = result.scalar_one_or_none()

        if lot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lot not found",
            )

        if lot.status != LotStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Цю річ уже забрав інший покупець",
            )

        now = datetime.now(UTC)
        lot.status = LotStatus.TAKEN
        lot.taken_at = now
        lot.final_price = lot.current_price
        if current_user:
            lot.winner_id = current_user.id

        claim_code = generate_claim_code()
        savings_from_ceiling = max(Decimal("0.00"), lot.start_price - lot.current_price)
        if lot.start_price > 0:
            savings_percentage = int(round(float(savings_from_ceiling / lot.start_price * 100)))
        else:
            savings_percentage = 0

        order = Order(
            lot_id=lot.id,
            user_id=current_user.id if current_user else None,
            claim_code=claim_code,
            final_price=lot.current_price,
            savings_from_ceiling=savings_from_ceiling,
            savings_percentage=savings_percentage,
            status=OrderStatus.PAID,
            buyer_contact=buyer_contact,
            shipping_address=shipping_addr,
            payment_reference=payment_ref,
        )
        db.add(order)
        try:
            await db.commit()
            await db.refresh(order)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Цю річ уже забрав інший покупець",
            ) from None

        lot_taken_event = LotTakenEvent(
            event="LOT_TAKEN",
            lot_id=lot.id,
            final_price=lot.current_price,
            taken_at=now,
            savings_percentage=savings_percentage,
        )
        await publish_message(
            "auction_events",
            serialize_auction_event(lot_taken_event),
        )

        return TakeLotResponse(
            claim_code=order.claim_code,
            order=OrderRead.model_validate(order),
        )


@router.get("/{lot_id}", response_model=LotRead)
async def get_lot(
    lot_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Lot:
    query = select(Lot).options(selectinload(Lot.images)).where(Lot.id == lot_id)
    result = await db.execute(query)
    lot = result.scalar_one_or_none()
    if lot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot not found",
        )
    return lot


@router.get("", response_model=list[LotRead])
async def list_lots(
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: Annotated[LotStatus | None, Query(alias="status")] = None,
) -> list[Lot]:
    query = select(Lot).options(selectinload(Lot.images))
    if status_filter:
        query = query.where(Lot.status == status_filter)
    query = query.order_by(Lot.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())
