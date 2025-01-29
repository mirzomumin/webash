import logging
from docker import DockerClient
from docker.models.containers import Container
from fastapi import WebSocket, WebSocketDisconnect
from src.config import settings
from src.core.base.exceptions import ContainerUnavailable
from src.core.base.ws import manager as ws_manager
from src.core.base.container import manager as container_manager
from src.core.base.proxy import DockerWebSocketProxy
from src.core.models.user import User

docker_client = DockerClient(base_url=settings.DOCKER_API_URL, max_pool_size=100)
logger = logging.getLogger("webashapp")


class ConsoleService:
    @classmethod
    async def run(cls, *, user: User, websocket: WebSocket):
        user_id = user.id
        await ws_manager.connect(user_id=user_id, websocket=websocket)

        try:
            container: Container = container_manager.create(
                user=user,
                docker_client=docker_client,
            )
            container_manager.add(user_id=user_id, container=container)

            proxy = DockerWebSocketProxy(
                websocket=websocket,
                container=container,
            )

            # Handle the WebSocket connection
            await proxy.handle_proxy()

        except WebSocketDisconnect:
            ws_manager.disconnect(user_id=user_id)

        except ContainerUnavailable:
            ws_manager.disconnect(user_id=user_id)

        except Exception as e:
            logger.error(f"Unexpected exception: {e}")
            ws_manager.disconnect(user_id=user_id)
