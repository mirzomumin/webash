import asyncio
import logging
import websockets
from fastapi import WebSocket, WebSocketDisconnect
from docker.models.containers import Container
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets.asyncio.client import ClientConnection
from src.config import settings


logger = logging.getLogger("webashapp")
DOCKER_WS_URL = settings.DOCKER_WS_URL  # Replace with your Docker API endpoint
# DOCKER_API_URL = settings.DOCKER_SOCKET_PATH


class DockerWebSocketProxy:
    def __init__(self, *, websocket: WebSocket, container: Container):
        self.websocket = websocket
        self.container = container

    async def handle_proxy(self):
        container_id = self.container.id
        docker_ws_url = f"{DOCKER_WS_URL}/containers/{container_id}/attach/ws?stream=1&stdout=1&stdin=1&logs=1&stderr=1"

        try:
            # Connect to the Docker WebSocket
            async with websockets.connect(docker_ws_url) as docker_ws:
                # Forward messages bidirectionally
                await asyncio.gather(
                    self._write_to_socket(docker_ws),  # Client -> Docker
                    self._read_from_socket(docker_ws),  # Docker -> Client
                )
        except ConnectionClosedError:
            logger.error("WebSocket connection closed")
            raise
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            self.container.remove(force=True)
            await self.websocket.close()

    async def _write_to_socket(self, docker_ws: ClientConnection):
        try:
            while True:
                msg = await self.websocket.receive_text()
                await docker_ws.send(msg, text=False)
        except (WebSocketDisconnect, ConnectionClosedError):
            logger.error("Writing to docker socket stopped")
            raise
        except Exception as e:
            logger.error(f"Writing to docker socket error: {e}")
            raise

    async def _read_from_socket(self, docker_ws: ClientConnection):
        try:
            while True:
                data = await docker_ws.recv()
                logger.info(f'Data: "{data}" from container "{self.container.id}"')
                await self.websocket.send_bytes(data)
        except (WebSocketDisconnect, ConnectionClosedError, ConnectionClosedOK):
            logger.error("Reading from docker socket stopped")
            raise
        except Exception as e:
            logger.error(f"Reading from docker socket error: {e}")
            raise
