# Dutch Auction Archive — Core Technical Specification
Version: 1.0.0

## 1. Overview
The platform is a specialized marketplace for archival fashion (Helmut Lang, Raf Simons, Maison Martin Margiela, Undercover, Comme des Garcons, Yohji Yamamoto) powered by a Dutch Auction model.
In this auction model, every lot starts at an initial peak price and drops at discrete, configurable intervals (ticks) until a buyer executes an immediate atomic purchase or the lot reaches its reserve (floor) price.

## 2. Technical Stack
- Backend: Python 3.12, uv, FastAPI, SQLAlchemy 2.0 (asyncio), asyncpg, Alembic, Pydantic v2, Pydantic-Settings
- Background Worker: Celery, Celery Beat, Redis (Broker & Result Backend)
- Real-Time Communication: FastAPI WebSockets + Redis Pub/Sub
- Storage: MinIO (S3-compatible) with private/public bucket configuration
- Database: PostgreSQL 16
- Frontend: React 19, TypeScript, Vite, Tailwind CSS, TanStack Query, React Router, Lucide Icons
- Quality & Standards: Ruff, Mypy (strict), Pytest, ESLint 9, Prettier, Pre-commit
- Strict Rule: Zero comments throughout the entire codebase. Code must be self-documenting with strict static typing.

## 3. Data Schema & Contracts

### 3.1 Enumerations
- LotStatus: `DRAFT`, `SCHEDULED`, `ACTIVE`, `SOLD`, `EXPIRED`, `CANCELLED`
- LotCategory: `OUTERWEAR`, `TOPS`, `BOTTOMS`, `FOOTWEAR`, `ACCESSORIES`
- OrderStatus: `PAID`, `FULFILLED`, `CANCELLED`
- UserRole: `CUSTOMER`, `ADMIN`

### 3.2 Tables

#### `users`
- `id`: UUID (Primary Key, default uuid4)
- `email`: String (Unique, Indexed, Not Null)
- `hashed_password`: String (Not Null)
- `full_name`: String (Nullable)
- `role`: Enum(UserRole) (Default: CUSTOMER, Not Null)
- `is_active`: Boolean (Default: True, Not Null)
- `created_at`: DateTime(timezone=True) (Server Default: now(), Not Null)
- `updated_at`: DateTime(timezone=True) (Server Default: now(), onupdate: now(), Not Null)

#### `lots`
- `id`: UUID (Primary Key, default uuid4)
- `title`: String (Not Null, Indexed)
- `brand`: String (Not Null, Indexed)
- `designer`: String (Not Null)
- `season`: String (Not Null)
- `year`: Integer (Not Null, Indexed)
- `collection_name`: String (Nullable)
- `category`: Enum(LotCategory) (Not Null, Indexed)
- `subcategory`: String (Not Null)
- `tagged_size`: String (Not Null)
- `fits_like`: String (Not Null)
- `measurements`: JSONB (Not Null, schema: {pit_to_pit, length, shoulders, sleeve, waist, inseam, hem})
- `materials`: JSONB (Not Null, schema: {outer, lining, hardware})
- `condition_rating`: Integer (Not Null, 1-10)
- `condition_details`: Text (Not Null)
- `country_of_origin`: String (Not Null)
- `provenance_notes`: Text (Nullable)
- `start_price`: Numeric(12, 2) (Not Null)
- `floor_price`: Numeric(12, 2) (Not Null)
- `current_price`: Numeric(12, 2) (Not Null, Indexed)
- `step_amount`: Numeric(12, 2) (Not Null)
- `interval_seconds`: Integer (Not Null, default 60)
- `status`: Enum(LotStatus) (Default: DRAFT, Not Null, Indexed)
- `started_at`: DateTime(timezone=True) (Nullable)
- `next_drop_at`: DateTime(timezone=True) (Nullable, Indexed)
- `sold_at`: DateTime(timezone=True) (Nullable)
- `sold_price`: Numeric(12, 2) (Nullable)
- `winner_id`: UUID (ForeignKey("users.id"), Nullable)
- `created_at`: DateTime(timezone=True) (Server Default: now(), Not Null)
- `updated_at`: DateTime(timezone=True) (Server Default: now(), onupdate: now(), Not Null)

#### `lot_images`
- `id`: UUID (Primary Key, default uuid4)
- `lot_id`: UUID (ForeignKey("lots.id", ondelete="CASCADE"), Not Null, Indexed)
- `image_url`: String (Not Null)
- `sort_order`: Integer (Default: 0, Not Null)
- `caption`: String (Nullable)
- `created_at`: DateTime(timezone=True) (Server Default: now(), Not Null)

#### `orders`
- `id`: UUID (Primary Key, default uuid4)
- `lot_id`: UUID (ForeignKey("lots.id"), Unique, Not Null)
- `user_id`: UUID (ForeignKey("users.id"), Not Null, Indexed)
- `final_price`: Numeric(12, 2) (Not Null)
- `status`: Enum(OrderStatus) (Default: PAID, Not Null)
- `shipping_address`: JSONB (Not Null, schema: {full_name, phone, address_line, city, postal_code, country})
- `payment_reference`: String (Not Null)
- `created_at`: DateTime(timezone=True) (Server Default: now(), Not Null)

## 4. API Endpoints

### 4.1 Authentication (`/api/v1/auth`)
- `POST /register`: Request `{email, password, full_name}`, Response `{access_token, token_type, user}`
- `POST /login`: Request `{username (email), password}`, Response `{access_token, token_type, user}`
- `GET /me`: Header `Authorization: Bearer <token>`, Response `UserResponse`

### 4.2 Lots (`/api/v1/lots`)
- `GET /`: Query `{category, brand, status, search, limit, offset}`, Response `List[LotSummaryResponse]`
- `GET /{id}`: Response `LotDetailResponse` with images and real-time auction status
- `POST /{id}/buy`: Atomic lock `SELECT ... FOR UPDATE`, Request `{shipping_address}`, Response `OrderResponse`

### 4.3 Admin (`/api/v1/admin`)
- Guard: Requires user with role `ADMIN` or admin credentials verification
- `POST /lots`: Create new archive lot with full metadata
- `POST /lots/{id}/images`: Upload multi-angle photos directly to MinIO
- `POST /lots/{id}/start`: Activate auction and schedule drops
- `POST /lots/{id}/cancel`: Cancel active lot
- `GET /orders`: List all orders and winning buyers
- `POST /seed`: Trigger database seeding with authentic archive lots and MinIO photos

### 4.4 WebSockets (`/api/v1/ws`)
- `WS /api/v1/ws/auctions`: Real-time duplex feed
  - Event `PRICE_TICK`: `{type: "PRICE_TICK", lot_id: UUID, current_price: Decimal, next_drop_at: ISO8601}`
  - Event `LOT_SOLD`: `{type: "LOT_SOLD", lot_id: UUID, winner_id: UUID, sold_price: Decimal}`
  - Event `LOT_EXPIRED`: `{type: "LOT_EXPIRED", lot_id: UUID, final_price: Decimal}`

## 5. Background Tasks (Celery & Redis)
- Periodic Task `process_auction_ticks`: Runs every 5 seconds.
  Queries all lots with `status = ACTIVE` and `next_drop_at <= now()`.
  Decrements `current_price = max(floor_price, current_price - step_amount)`.
  If `current_price == floor_price`, transitions status to `EXPIRED` if configured, or holds at reserve.
  Updates `next_drop_at = now() + interval_seconds`.
  Publishes JSON payload to Redis channel `auction_events`.

## 6. Slicing & Quality Guidelines
- All code must pass `ruff check`, `ruff format --check`, `mypy --strict`, `pytest`, `eslint`, and `npm run typecheck`.
- Absolute zero code comments in Python, TypeScript, and React components.
- Conventional commits required on every slice and sub-slice: `type(slice-X.Y): description`.
