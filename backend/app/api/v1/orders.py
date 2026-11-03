from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.lot import Lot
from app.models.order import Order
from app.schemas.order import OrderWithLotRead

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/lookup", response_model=OrderWithLotRead)
async def lookup_order(
    code: Annotated[str, Query(min_length=1)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Order:
    clean_code = code.strip().upper()
    query = (
        select(Order)
        .options(selectinload(Order.lot).selectinload(Lot.images))
        .where(Order.claim_code == clean_code)
    )
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Замовлення за вказаним чек-кодом не знайдено",
        )
    return order


@router.get("/ledger", response_model=list[OrderWithLotRead])
async def get_ledger(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Order]:
    query = (
        select(Order)
        .options(selectinload(Order.lot).selectinload(Lot.images))
        .order_by(Order.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())
