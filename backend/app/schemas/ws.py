import json
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


def _format_datetime(dt: datetime) -> str:
    iso = dt.isoformat()
    if iso.endswith("+00:00"):
        return iso[:-6] + "Z"
    return iso


class PriceTickEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event: Literal["PRICE_TICK"] = "PRICE_TICK"
    lot_id: uuid.UUID
    current_price: Decimal
    floor_price: Decimal
    step_amount: Decimal
    next_drop_at: datetime

    def to_dict(self) -> dict[str, object]:
        return {
            "event": self.event,
            "lot_id": str(self.lot_id),
            "current_price": float(self.current_price),
            "floor_price": float(self.floor_price),
            "step_amount": float(self.step_amount),
            "next_drop_at": _format_datetime(self.next_drop_at),
        }


class LotTakenEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event: Literal["LOT_TAKEN"] = "LOT_TAKEN"
    lot_id: uuid.UUID
    final_price: Decimal
    taken_at: datetime
    savings_percentage: int

    def to_dict(self) -> dict[str, object]:
        return {
            "event": self.event,
            "lot_id": str(self.lot_id),
            "final_price": float(self.final_price),
            "taken_at": _format_datetime(self.taken_at),
            "savings_percentage": self.savings_percentage,
        }


class LotExpiredEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event: Literal["LOT_EXPIRED"] = "LOT_EXPIRED"
    lot_id: uuid.UUID
    floor_price: Decimal
    expired_at: datetime

    def to_dict(self) -> dict[str, object]:
        return {
            "event": self.event,
            "lot_id": str(self.lot_id),
            "floor_price": float(self.floor_price),
            "expired_at": _format_datetime(self.expired_at),
        }


AuctionEvent = PriceTickEvent | LotTakenEvent | LotExpiredEvent


def serialize_auction_event(event: AuctionEvent) -> str:
    return json.dumps(event.to_dict())
