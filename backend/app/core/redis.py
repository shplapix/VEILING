from __future__ import annotations

import contextlib
from collections.abc import Callable, Coroutine
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

_redis_client: aioredis.Redis[str] | None = None
_local_listeners: list[Callable[[str, str], Coroutine[Any, Any, None]]] = []


def get_redis_client() -> aioredis.Redis[str]:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _redis_client


def register_local_listener(
    listener: Callable[[str, str], Coroutine[Any, Any, None]],
) -> None:
    if listener not in _local_listeners:
        _local_listeners.append(listener)


def unregister_local_listener(
    listener: Callable[[str, str], Coroutine[Any, Any, None]],
) -> None:
    if listener in _local_listeners:
        _local_listeners.remove(listener)


async def publish_to_channel(
    channel: str,
    message: str,
    redis_client: aioredis.Redis[str] | None = None,
) -> bool:
    client = redis_client or get_redis_client()
    try:
        await client.publish(channel, message)
        return True
    except Exception:
        return False


async def publish_message(
    channel: str,
    message: str,
    redis_client: aioredis.Redis[str] | None = None,
) -> None:
    published = await publish_to_channel(channel, message, redis_client)
    if not published:
        for listener in list(_local_listeners):
            with contextlib.suppress(Exception):
                await listener(channel, message)


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        client = _redis_client
        _redis_client = None
        with contextlib.suppress(Exception):
            close_fn = getattr(client, "aclose", client.close)
            await close_fn()
