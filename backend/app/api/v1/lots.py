import asyncio
import secrets
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_optional_current_user
from app.core.redis import publish_message
from app.models.enums import LotStatus, OrderStatus
from app.models.lot import Lot
from app.models.order import Order, generate_claim_code
from app.models.user import User
from app.schemas.lot import LotRead
from app.schemas.order import OrderRead, TakeLotRequest, TakeLotResponse
from app.schemas.ws import LotTakenEvent, serialize_auction_event

router = APIRouter(prefix="/lots", tags=["lots"])

_lot_locks: dict[uuid.UUID, asyncio.Lock] = {}
_lot_locks_guard = asyncio.Lock()


async def _get_lot_lock(lot_id: uuid.UUID) -> asyncio.Lock:
    async with _lot_locks_guard:
        if lot_id not in _lot_locks:
            _lot_locks[lot_id] = asyncio.Lock()
        return _lot_locks[lot_id]


@router.post("/{lot_id}/take", response_model=TakeLotResponse)
async def take_lot(
    lot_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    payload: TakeLotRequest | None = None,
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
) -> TakeLotResponse:
    req = payload or TakeLotRequest()
    buyer_contact = (
        req.buyer_contact.strip()
        if req.buyer_contact and req.buyer_contact.strip()
        else (current_user.email if current_user else "guest@veiling.archive")
    )
    payment_ref = (
        req.payment_reference if req.payment_reference else f"PAY-{secrets.token_hex(6).upper()}"
    )
    shipping_addr = (
        req.shipping_address if req.shipping_address else {"delivery": "pending_contact"}
    )

    lock = await _get_lot_lock(lot_id)
    async with lock:
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
        await db.commit()
        await db.refresh(order)

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
