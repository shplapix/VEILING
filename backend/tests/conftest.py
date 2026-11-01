import uuid
from collections.abc import AsyncIterator
from typing import Any

import pytest
from botocore.exceptions import ClientError
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
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


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class FakeS3Service:
    def __init__(self) -> None:
        self.storage: dict[str, tuple[bytes, str]] = {}
        self.public_url = "http://localhost:9000/archive-lots"

    def get_public_url(self, key: str) -> str:
        base = self.public_url.rstrip("/")
        clean_key = key.lstrip("/")
        return f"{base}/{clean_key}"

    def validate_content_type(self, content_type: str) -> str:
        clean_type = content_type.split(";")[0].lower().strip()
        if clean_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"Invalid image type '{content_type}'")
        return ALLOWED_IMAGE_TYPES[clean_type]

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
            raise ClientError(
                {"Error": {"Code": "NoSuchKey", "Message": f"Key {key} not found"}},
                "GetObject",
            )
        return self.storage[key]


@pytest.fixture
def fake_s3() -> FakeS3Service:
    return FakeS3Service()


@pytest.fixture
async def db_engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def db_session_factory(db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
async def db_session(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with db_session_factory() as session:
        yield session


@pytest.fixture
async def client(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
