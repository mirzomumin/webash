from fastapi import APIRouter, Depends, WebSocket
from src.core.utils.auth import jwt_authentication
from src.core.models.user import User
from src.api.v1.services.console import ConsoleService

router = APIRouter(prefix="/console")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user: User = Depends(jwt_authentication),
):
    await ConsoleService.run(user=user, websocket=websocket)
