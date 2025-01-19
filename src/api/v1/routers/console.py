from docker import DockerClient
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.config import settings
from src.core.utils.exceptions import ContainerUnavailable
from src.core.utils.ws import manager
from src.core.utils.proxy import DockerWebSocketProxy
from src.core.utils.auth import jwt_authentication
from src.core.models.user import User

router = APIRouter(prefix="/console")
docker_client = DockerClient(base_url=settings.DOCKER_SOCKET_PATH)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user: User = Depends(jwt_authentication),
):
    await manager.connect(websocket)
    try:
        proxy = DockerWebSocketProxy(websocket, docker_client, user)
        await proxy.handle_proxy()

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except ContainerUnavailable:
        msg = "Terminal stopped. Reload the page.".encode()
        await websocket.send_bytes(msg)
        manager.disconnect(websocket)
        await websocket.close()

    except Exception:
        msg = "Unexpected error. Reload the page.".encode()
        await websocket.send_bytes(msg)
        manager.disconnect(websocket)
        await websocket.close()
