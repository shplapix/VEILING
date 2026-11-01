import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import LotCategory, LotStatus


class LotImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    image_url: str
    sort_order: int
    display_order: int = 0
    caption: str | None = None


class LotImageCreate(BaseModel):
    image_url: str = Field(..., min_length=1, max_length=1024)
    sort_order: int = 0
    display_order: int | None = None
    caption: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def sync_display_order(self) -> "LotImageCreate":
        if self.display_order is not None and self.sort_order == 0:
            self.sort_order = self.display_order
        elif self.display_order is None:
            self.display_order = self.sort_order
        return self


class ImageUploadResponse(BaseModel):
    image_url: str
    key: str


class LotCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    brand: str = Field(..., min_length=1, max_length=100)
    designer: str | None = Field(default=None, max_length=100)
    season: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1900, le=2100)
    collection_name: str | None = Field(default=None, max_length=150)
    category: LotCategory
    subcategory: str = Field(..., min_length=1, max_length=100)
    tagged_size: str = Field(..., min_length=1, max_length=50)
    fits_like: str = Field(..., min_length=1, max_length=50)
    measurements: dict[str, Any] = Field(default_factory=dict)
    materials: dict[str, Any] = Field(default_factory=dict)
    condition_rating: int = Field(..., ge=1, le=10)
    condition_details: str = Field(..., min_length=1)
    country_of_origin: str = Field(..., min_length=1, max_length=100)
    provenance_notes: str | None = None
    seller_location: str = Field(default="Амстердам, Нідерланди", max_length=100)
    shipping_notes: str = Field(
        default="Застрахована кур'єрська доставка по Європі та Україні (3–5 робочих днів)"
    )
    start_price: Decimal = Field(..., gt=Decimal("0.00"))
    floor_price: Decimal = Field(..., gt=Decimal("0.00"))
    step_amount: Decimal = Field(..., gt=Decimal("0.00"))
    interval_seconds: int = Field(default=60, gt=0)
    status: LotStatus = Field(default=LotStatus.ACTIVE)
    images: list[LotImageCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_prices_and_designer(self) -> "LotCreate":
        if self.start_price < self.floor_price:
            raise ValueError(
                "Стеля ціни (start_price) повинна бути більшою або рівною за підлогу (floor_price)"
            )
        if not self.designer:
            self.designer = self.brand
        return self


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
