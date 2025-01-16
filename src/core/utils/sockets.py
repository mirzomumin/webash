import asyncio
import socket
from fastapi import WebSocket, WebSocketDisconnect


DOCKER_SOCKET_PATH = "/var/run/docker.sock"


async def proxy_docker_socket(websocket: WebSocket):
    """Handles bidirectional communication between the client and Docker socket."""
    # Create a connection to the Docker Unix socket
    docker_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    docker_socket.connect(DOCKER_SOCKET_PATH)

    loop = asyncio.get_event_loop()

    # Construct the HTTP request for attaching to the container
    container_id = "103b57e7cec9"
    query = "stream=1&stdout=1&stdin=1&logs=1"
    request = (
        f"POST /containers/{container_id}/attach?{query} HTTP/1.1\r\n"
        f"Host: docker\r\n"
        f"Connection: Upgrade\r\n"
        f"Upgrade: tcp\r\n\r\n"
    )
    docker_socket.sendall(request.encode())

    async def read_from_socket():
        """Read data from Docker socket and send it to WebSocket."""
        while True:
            try:
                data = await loop.run_in_executor(None, docker_socket.recv, 4096)
                print(f"DATA FROM SOCKET: {data.decode()}")
                if not data:
                    break
                await websocket.send_bytes(data)
            except Exception as e:
                print(f"Error reading from Docker socket: {e}")
                break

    async def write_to_socket():
        """Read data from WebSocket and send it to Docker socket."""
        while True:
            try:
                # Receive data from WebSocket
                message = await websocket.receive()
                if "bytes" in message:
                    print(f"DATA TYPE: {message}")
                    data = message["bytes"]  # Binary data
                elif "text" in message:
                    print(f"DATA TYPE: {message}")
                    data = message["text"].encode()  # Text data, encode to bytes
                else:
                    print("Unsupported message type from WebSocket.")
                    continue
                await loop.run_in_executor(None, docker_socket.sendall, data)
            except WebSocketDisconnect:
                print("WebSocket disconnected.")
                break
            except Exception as e:
                print(f"Error writing to Docker socket: {e}")
                break

    # Run the tasks concurrently
    await asyncio.gather(read_from_socket(), write_to_socket())

    # Cleanup
    docker_socket.close()


# @app.websocket("/proxy")
# async def docker_proxy(websocket: WebSocket):
#     """WebSocket endpoint to proxy communication to Docker socket."""
#     await websocket.accept()
#     await proxy_docker_socket(websocket)
