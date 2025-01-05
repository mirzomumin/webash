from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.base.utils.ws import manager
from src.base.utils.shell import run_shell_cmd

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    # user: User = Depends(jwt_authentication),
):
    # client_id = user.id
    client_id = 1
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
        await manager.broadcast(f"Client #{client_id} left the chat")
