import logging
from docker import DockerClient
from docker.models.containers import Container
from fastapi import WebSocket, WebSocketDisconnect
from src.config import settings
from src.core.utils.exceptions import ContainerUnavailable
from src.core.utils.ws import manager as ws_manager
from src.core.utils.container import manager as container_manager
from src.core.utils.proxy import DockerWebSocketProxy
from src.core.models.user import User

docker_client = DockerClient(base_url=settings.DOCKER_SOCKET_PATH, max_pool_size=100)
logger = logging.getLogger("webashapp")


class ConsoleService:
    @classmethod
    async def run(cls, *, user: User, websocket: WebSocket):
        user_id = user.id

        # Handle the WebSocket connection
        await ws_manager.connect(user_id=user_id, websocket=websocket)

        try:
            container: Container = await container_manager.create(
                user=user,
                docker_client=docker_client,
            )
            container_manager.add(user_id=user_id, container=container)

            proxy = DockerWebSocketProxy(
                websocket=websocket,
                container=container,
            )

            await proxy.handle_proxy()

        except WebSocketDisconnect:
            ws_manager.disconnect(user_id=user_id)

        except ContainerUnavailable:
            msg = "Terminal stopped. Reload the page.".encode()
            await websocket.send_bytes(msg)
            ws_manager.disconnect(user_id=user_id)

        except Exception as e:
            logger.error(f"Unexpected exception: {e}")
            msg = "Unexpected error. Reload the page.".encode()
            await websocket.send_bytes(msg)
            await websocket.close()
            ws_manager.disconnect(user_id=user_id)
