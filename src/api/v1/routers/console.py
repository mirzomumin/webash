from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.core.utils.ws import manager
from src.core.utils.sockets import DockerWebSocketProxy

router = APIRouter(prefix="/console")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    # user: User = Depends(jwt_authentication),
):
    await manager.connect(websocket)
    try:
        # client_id = user.id
        proxy = DockerWebSocketProxy(websocket, "e6329a9a8cfd")
        await proxy.handle_proxy()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
