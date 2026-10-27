from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    user_role_enum = sa.Enum(
        "CUSTOMER",
        "SELLER",
        "ADMIN",
        name="user_role",
    )
    lot_status_enum = sa.Enum(
        "DRAFT",
        "SCHEDULED",
        "ACTIVE",
        "TAKEN",
        "EXPIRED",
        "CANCELLED",
        name="lot_status",
    )
    lot_category_enum = sa.Enum(
        "OUTERWEAR",
        "TOPS",
        "BOTTOMS",
        "FOOTWEAR",
        "ACCESSORIES",
        name="lot_category",
    )
    order_status_enum = sa.Enum(
        "PAID",
        "FULFILLED",
        "CANCELLED",
        name="order_status",
    )

    jsonb_type = sa.JSON().with_variant(postgresql.JSONB, "postgresql")
    uuid_type = sa.UUID(as_uuid=True)

    op.create_table(
        "users",
        sa.Column(
            "id",
            uuid_type,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", user_role_enum, nullable=False, server_default="SELLER"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "lots",
        sa.Column(
            "id",
            uuid_type,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("brand", sa.String(length=100), nullable=False),
        sa.Column("designer", sa.String(length=100), nullable=False),
        sa.Column("season", sa.String(length=50), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("collection_name", sa.String(length=150), nullable=True),
        sa.Column("category", lot_category_enum, nullable=False),
        sa.Column("subcategory", sa.String(length=100), nullable=False),
        sa.Column("tagged_size", sa.String(length=50), nullable=False),
        sa.Column("fits_like", sa.String(length=50), nullable=False),
        sa.Column("measurements", jsonb_type, nullable=False),
        sa.Column("materials", jsonb_type, nullable=False),
        sa.Column("condition_rating", sa.Integer(), nullable=False),
        sa.Column("condition_details", sa.Text(), nullable=False),
        sa.Column("country_of_origin", sa.String(length=100), nullable=False),
        sa.Column("provenance_notes", sa.Text(), nullable=True),
        sa.Column(
            "seller_location",
            sa.String(length=100),
            nullable=False,
            server_default="Амстердам, Нідерланди",
        ),
        sa.Column(
            "shipping_notes",
            sa.Text(),
            nullable=False,
            server_default=(
                "Застрахована кур'єрська доставка по Європі та Україні (3–5 робочих днів)"
            ),
        ),
        sa.Column("start_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("floor_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("current_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("step_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("interval_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("status", lot_status_enum, nullable=False, server_default="DRAFT"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_drop_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("final_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("winner_id", uuid_type, sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "condition_rating >= 1 AND condition_rating <= 10",
            name="ck_lot_condition_rating",
        ),
        sa.CheckConstraint(
            "floor_price > 0 AND start_price >= floor_price",
            name="ck_lot_price_bounds",
        ),
        sa.CheckConstraint(
            "step_amount > 0",
            name="ck_lot_step_amount",
        ),
        sa.CheckConstraint(
            "interval_seconds > 0",
            name="ck_lot_interval_seconds",
        ),
    )
    op.create_index("ix_lots_title", "lots", ["title"])
    op.create_index("ix_lots_brand", "lots", ["brand"])
    op.create_index("ix_lots_year", "lots", ["year"])
    op.create_index("ix_lots_category", "lots", ["category"])
    op.create_index("ix_lots_current_price", "lots", ["current_price"])
    op.create_index("ix_lots_status", "lots", ["status"])
    op.create_index("ix_lots_next_drop_at", "lots", ["next_drop_at"])
    op.create_index("ix_lots_winner_id", "lots", ["winner_id"])

    op.create_table(
        "lot_images",
        sa.Column(
            "id",
            uuid_type,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "lot_id",
            uuid_type,
            sa.ForeignKey("lots.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("image_url", sa.String(length=1024), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("caption", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_lot_images_lot_id", "lot_images", ["lot_id"])

    op.create_table(
        "price_ticks",
        sa.Column(
            "id",
            uuid_type,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "lot_id",
            uuid_type,
            sa.ForeignKey("lots.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_price_ticks_lot_id", "price_ticks", ["lot_id"])
    op.create_index("ix_price_ticks_created_at", "price_ticks", ["created_at"])

    op.create_table(
        "orders",
        sa.Column(
            "id",
            uuid_type,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "lot_id",
            uuid_type,
            sa.ForeignKey("lots.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("user_id", uuid_type, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("claim_code", sa.String(length=64), nullable=False),
        sa.Column("final_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "savings_from_ceiling",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column("savings_percentage", sa.Integer(), nullable=False),
        sa.Column("status", order_status_enum, nullable=False, server_default="PAID"),
        sa.Column("buyer_contact", sa.String(length=255), nullable=False),
        sa.Column("shipping_address", jsonb_type, nullable=False),
        sa.Column("payment_reference", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_orders_claim_code", "orders", ["claim_code"], unique=True)
    op.create_index("ix_orders_user_id", "orders", ["user_id"])


def downgrade() -> None:
    op.drop_table("orders")
    op.drop_table("price_ticks")
    op.drop_table("lot_images")
    op.drop_table("lots")
    op.drop_table("users")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="order_status").drop(bind, checkfirst=True)
        sa.Enum(name="lot_category").drop(bind, checkfirst=True)
        sa.Enum(name="lot_status").drop(bind, checkfirst=True)
        sa.Enum(name="user_role").drop(bind, checkfirst=True)
