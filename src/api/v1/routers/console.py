import docker
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.core.utils.ws import manager
from src.core.utils.sockets import proxy_docker_socket

router = APIRouter(prefix="/console")


# DOCKER_SOCK = "/var/run/docker.sock"

# Initialize Docker client
# docker_client = docker.DockerClient(base_url=f"unix://{DOCKER_SOCK}")  # For Unix socket
client = docker.from_env()


# @router.websocket("/ws")
@router.websocket("/containers/{container_id}/attach/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    container_id: str,
    # user: User = Depends(jwt_authentication),
):
    try:
        # client_id = user.id
        await manager.connect(websocket)
        # await websocket.accept()
        await proxy_docker_socket(websocket)

    # Connect to the Docker API
    # docker_client = docker.from_env()
    # try:
    # container = docker_client.containers.get(container_id)
    # if container.status != "running":
    #     await websocket.close(code=1001, reason="Container is not running.")
    #     return

    # while True:
    #     cmd = await websocket.receive_text()
    #     await websocket.send_text(cmd + '\r\n')

    # Attach to the container
    # docker_socket = container.attach_socket(params={
    #     "stdin": True, "stdout": True, "stream": True, "logs": True
    # })

    # loop = asyncio.get_event_loop()

    # async def read_from_container():
    #     while True:
    #         data = docker_socket.read(1024)
    #         if data:
    #             await websocket.send_bytes(data)
    #         await asyncio.sleep(0.01)

    # async def write_to_container():
    #     while True:
    #         try:
    #             data = await websocket.receive_text()
    #             docker_socket.write(data.decode())
    #         except WebSocketDisconnect:
    #             break

    # while True:
    #     cmd = await websocket.receive_text()

    # Run the tasks concurrently
    # await asyncio.gather(read_from_container(), write_to_container())
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # Properly close the process
        # process.stdin.write("exit\n".encode())
        # await process.stdin.drain()
        # await process.wait()
        # delete_process(client_id)
        # await manager.broadcast(f"Client #{client_id} left the chat")
