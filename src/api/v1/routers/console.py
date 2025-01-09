from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.core.utils.ws import manager
from src.core.utils.shell import run_shell_cmd
from src.core.utils.auth import jwt_authentication

router = APIRouter(prefix="/console")


@router.websocket("/ws", dependencies=[Depends(jwt_authentication)])
async def websocket_endpoint(
    websocket: WebSocket,
):
    # client_id = user.id
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Stream data to the client
            await run_shell_cmd(data, websocket)
            # await websocket.iter_scope(generate_data())
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{client_id} left the chat")
