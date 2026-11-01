import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OrderStatus


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


class TakeLotRequest(BaseModel):
    buyer_contact: str = "guest@veiling.archive"
    shipping_address: dict[str, Any] = Field(default_factory=dict)
    payment_reference: str | None = None


class TakeLotResponse(BaseModel):
    claim_code: str
    order: OrderRead
