import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    UUID,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import LotCategory, LotStatus

if TYPE_CHECKING:
    from app.models.lot_image import LotImage
    from app.models.order import Order
    from app.models.price_tick import PriceTick
    from app.models.user import User


class Lot(Base):
    __tablename__ = "lots"
    __table_args__ = (
        CheckConstraint(
            "condition_rating >= 1 AND condition_rating <= 10",
            name="ck_lot_condition_rating",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    brand: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    designer: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    season: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    collection_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    category: Mapped[LotCategory] = mapped_column(
        Enum(
            LotCategory,
            name="lot_category",
            native_enum=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )
    subcategory: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    tagged_size: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    fits_like: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    measurements: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    materials: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    condition_rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    condition_details: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    country_of_origin: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    provenance_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    seller_location: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Амстердам, Нідерланди",
    )
    shipping_notes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Застрахована кур'єрська доставка по Європі та Україні (3–5 робочих днів)",
    )
    start_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    floor_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    current_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        index=True,
    )
    step_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    interval_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=60,
    )
    status: Mapped[LotStatus] = mapped_column(
        Enum(
            LotStatus,
            name="lot_status",
            native_enum=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=LotStatus.DRAFT,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    next_drop_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    taken_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    final_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    winner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    winner: Mapped["User | None"] = relationship(
        "User",
        back_populates="lots_won",
        foreign_keys=[winner_id],
    )
    images: Mapped[list["LotImage"]] = relationship(
        "LotImage",
        back_populates="lot",
        cascade="all, delete-orphan",
        order_by="LotImage.sort_order",
    )
    order: Mapped["Order | None"] = relationship(
        "Order",
        back_populates="lot",
        uselist=False,
    )
    price_ticks: Mapped[list["PriceTick"]] = relationship(
        "PriceTick",
        back_populates="lot",
        cascade="all, delete-orphan",
        order_by="PriceTick.created_at",
    )
