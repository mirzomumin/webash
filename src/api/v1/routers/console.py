from docker import DockerClient
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.config import settings
from src.core.utils.ws import manager
from src.core.utils.proxy import DockerWebSocketProxy

router = APIRouter(prefix="/console")
docker_client = DockerClient(base_url=f"unix://{settings.DOCKER_SOCKET_PATH}")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    # user: User = Depends(jwt_authentication),
):
    await manager.connect(websocket)
    try:
        # client_id = user.id
        proxy = DockerWebSocketProxy(websocket, docker_client)
        await proxy.handle_proxy()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
