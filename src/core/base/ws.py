import asyncio
import logging
from uuid import UUID
from fastapi import WebSocket
from fastapi.websockets import WebSocketState

logger = logging.getLogger("webashapp")


class ConnectionManager:
    """WebSocket connection manager"""

    def __init__(self):
        self.active_connections: dict[UUID, WebSocket] = {}
        self.locks: dict[UUID, asyncio.Lock] = {}

    def get_websocket(self, *, user_id: UUID) -> WebSocket | None:
        return self.active_connections.get(user_id)

    async def connect(self, *, user_id: UUID, websocket: WebSocket):
        # Get or create a lock for the user
        if user_id not in self.locks:
            self.locks[user_id] = asyncio.Lock()

        async with self.locks[user_id]:
            # Check for an existing connection
            if user_id not in self.active_connections:
                # Accept the new WebSocket connection
                await self._connect(user_id=user_id, websocket=websocket)
                return

            old_websocket = self.active_connections[user_id]
            if old_websocket.client_state == WebSocketState.CONNECTED:
                # Interrupt the previous connection
                await old_websocket.close(
                    code=1008, reason="New connection established"
                )
                logger.info(f"Closed previous connection for user {user_id}")

            await self._connect(user_id=user_id, websocket=websocket)

    async def _connect(self, *, user_id: UUID, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"New connection {websocket} established for user {user_id}")

    def disconnect(self, *, user_id: UUID):
        ws = self.get_websocket(user_id=user_id)
        logger.info(f"Connection {ws} is going to be removed for user {user_id}")
        if ws is not None and ws.client_state == WebSocketState.DISCONNECTED:
            logger.info(
                f"Connection {self.active_connections[user_id]} removed for user {user_id}"
            )
            del self.active_connections[user_id]

    async def send_personal_message(self, *, message: str, user_id: UUID):
        websocket = self.active_connections[user_id]
        await websocket.send_text(message)

    async def broadcast(self, *, message: str):
        for _, connection in self.active_connections:
            await connection.send_text(message)


# Get single instance of connection manager
manager = ConnectionManager()
