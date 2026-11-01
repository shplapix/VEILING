import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import LotCategory, LotStatus


class LotImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    image_url: str
    sort_order: int
    caption: str | None = None


class LotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    brand: str
    designer: str
    season: str
    year: int
    collection_name: str | None = None
    category: LotCategory
    subcategory: str
    tagged_size: str
    fits_like: str
    measurements: dict[str, Any]
    materials: dict[str, Any]
    condition_rating: int
    condition_details: str
    country_of_origin: str
    provenance_notes: str | None = None
    seller_location: str
    shipping_notes: str
    start_price: Decimal
    floor_price: Decimal
    current_price: Decimal
    step_amount: Decimal
    interval_seconds: int
    status: LotStatus
    started_at: datetime | None = None
    next_drop_at: datetime | None = None
    taken_at: datetime | None = None
    final_price: Decimal | None = None
    winner_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    images: list[LotImageRead] = Field(default_factory=list)
