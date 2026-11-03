import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import OrderStatus
from app.schemas.lot import LotRead


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lot_id: uuid.UUID
    user_id: uuid.UUID | None
    claim_code: str
    final_price: Decimal
    savings_from_ceiling: Decimal
    savings_percentage: int
    status: OrderStatus
    buyer_contact: str
    shipping_address: dict[str, Any]
    payment_reference: str
    created_at: datetime


class OrderWithLotRead(OrderRead):
    lot: LotRead | None = None


class LedgerItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lot_id: uuid.UUID
    claim_code: str
    final_price: Decimal
    savings_from_ceiling: Decimal
    savings_percentage: int
    status: OrderStatus
    created_at: datetime
    lot: LotRead | None = None

    @field_validator("claim_code")
    @classmethod
    def mask_claim_code(cls, v: str) -> str:
        if len(v) >= 6:
            return f"{v[:6]}-****-****"
        return "V-****-****"


class TakeLotRequest(BaseModel):
    buyer_contact: str | None = None
    shipping_address: dict[str, Any] = Field(default_factory=dict)
    payment_reference: str | None = None


class TakeLotResponse(BaseModel):
    claim_code: str
    order: OrderRead
