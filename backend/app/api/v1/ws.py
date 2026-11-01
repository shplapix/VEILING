import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.redis import (
    get_redis_client,
    register_local_listener,
)

router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        async with self._lock:
            connections = list(self.active_connections)
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception:
                await self.disconnect(connection)

    @property
    def active_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()


async def _on_local_redis_message(channel: str, message: str) -> None:
    if channel == "auction_events":
        await manager.broadcast(message)


register_local_listener(_on_local_redis_message)


async def redis_pubsub_listener(
    conn_manager: ConnectionManager,
    stop_event: asyncio.Event,
) -> None:
    while not stop_event.is_set():
        try:
            client = get_redis_client()
            async with client.pubsub() as pubsub:
                await pubsub.subscribe("auction_events")
                while not stop_event.is_set():
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True,
                        timeout=1.0,
                    )
                    if message and message.get("type") == "message":
                        data = message.get("data")
                        if isinstance(data, str):
                            await conn_manager.broadcast(data)
                        elif isinstance(data, bytes):
                            await conn_manager.broadcast(data.decode("utf-8"))
        except Exception:
            await asyncio.sleep(1.0)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        await manager.disconnect(websocket)


@router.websocket("/ws/auction")
async def websocket_auction_endpoint(websocket: WebSocket) -> None:
    await websocket_endpoint(websocket)
