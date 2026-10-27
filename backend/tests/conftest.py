import uuid
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

import app.models as models
from app.api.deps import get_db
from app.core.database import Base
from app.core.s3 import ALLOWED_IMAGE_TYPES
from app.main import app

_ = models


class FakeS3Service:
    def __init__(self) -> None:
        self.storage: dict[str, tuple[bytes, str]] = {}
        self.public_url = "http://localhost:9000/archive-lots"

    def get_public_url(self, key: str) -> str:
        base = self.public_url.rstrip("/")
        clean_key = key.lstrip("/")
        return f"{base}/{clean_key}"

    def validate_content_type(self, content_type: str) -> str:
        normalized = content_type.lower().strip()
        if normalized not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"Invalid image type '{content_type}'")
        return ALLOWED_IMAGE_TYPES[normalized]

    async def ensure_bucket_exists(self) -> None:
        pass

    async def upload_image(
        self,
        file_data: bytes,
        content_type: str,
        prefix: str | None = None,
    ) -> tuple[str, str]:
        ext = self.validate_content_type(content_type)
        key = f"{uuid.uuid4()}{ext}"
        if prefix:
            key = f"{prefix.strip('/')}/{key}"
        self.storage[key] = (file_data, content_type)
        return key, self.get_public_url(key)

    async def delete_image(self, key: str) -> None:
        self.storage.pop(key, None)

    async def get_image(self, key: str) -> tuple[bytes, str]:
        if key not in self.storage:
            raise KeyError(f"Key {key} not found")
        return self.storage[key]


@pytest.fixture
def fake_s3() -> FakeS3Service:
    return FakeS3Service()


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
