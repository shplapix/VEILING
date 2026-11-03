import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.lot import Lot
from app.models.order import Order
from app.schemas.order import LedgerItemRead, OrderWithLotRead

router = APIRouter(prefix="/orders", tags=["orders"])

HOMOGLYPH_MAP = {
    "А": "A",
    "В": "B",
    "С": "C",
    "Е": "E",
    "Н": "H",
    "О": "O",
    "Р": "P",
    "Т": "T",
    "Х": "X",
}


def normalize_claim_code(raw: str) -> str:
    cleaned = raw.strip().upper()
    cleaned = re.sub(r"[\s\u200b\u00a0]+", "", cleaned)
    cleaned = cleaned.replace("—", "-").replace("–", "-").replace("−", "-")
    if cleaned.startswith("В-") or cleaned.startswith("B-"):
        cleaned = "V-" + cleaned[2:]
    elif cleaned.startswith("В") or cleaned.startswith("B"):
        cleaned = "V" + cleaned[1:]
    prefix = ""
    rest = cleaned
    if cleaned.startswith("V-"):
        prefix = "V-"
        rest = cleaned[2:]
    chars = [HOMOGLYPH_MAP.get(ch, ch) for ch in rest]
    return prefix + "".join(chars)


@router.get("/lookup", response_model=OrderWithLotRead)
async def lookup_order(
    code: Annotated[str, Query(min_length=1)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Order:
    clean_code = normalize_claim_code(code)
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


@router.get("/ledger", response_model=list[LedgerItemRead])
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
