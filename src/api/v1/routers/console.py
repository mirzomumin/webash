from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.core.models.user import User
from src.core.utils.ws import manager
from src.core.utils.shell import create_process, run_command, delete_process
from src.core.utils.auth import jwt_authentication

router = APIRouter(prefix="/console")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user: User = Depends(jwt_authentication),
):
    client_id = user.id
    await manager.connect(websocket)
    try:
        process = await create_process(client_id)
        print(f"THIS IS PROCESS!!!: {process}")
        while True:
            cmd = await websocket.receive_text()
            # Stream data to the client
            async for data in run_command(process=process, command=cmd):
                await websocket.send_text(data)
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # Properly close the process
        process.stdin.write("exit\n".encode())
        await process.stdin.drain()
        await process.wait()
        delete_process(client_id)
        # await manager.broadcast(f"Client #{client_id} left the chat")
