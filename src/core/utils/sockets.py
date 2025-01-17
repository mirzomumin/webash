import asyncio
import docker
import docker.errors
from fastapi import WebSocket
from docker.models.containers import Container


DOCKER_SOCKET_PATH = "/var/run/docker.sock"


# async def proxy_docker_socket(websocket: WebSocket):
#     """Handles bidirectional communication between the client and Docker socket."""
#     # Create a connection to the Docker Unix socket
#     docker_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#     docker_socket.connect(DOCKER_SOCKET_PATH)

#     loop = asyncio.get_event_loop()

#     # Construct the HTTP request for attaching to the container
#     container_id = "8b29680d555e"
#     query = "stream=1&stdout=1&stdin=1&logs=1"
#     request = (
#         f"POST /containers/{container_id}/attach?{query} HTTP/1.1\r\n"
#         f"Host: docker\r\n"
#         f"Connection: Upgrade\r\n"
#         f"Upgrade: tcp\r\n\r\n"
#     )
#     docker_socket.sendall(request.encode())

#     async def read_from_socket():
#         """Read data from Docker socket and send it to WebSocket."""
#         while True:
#             try:
#                 data = await loop.run_in_executor(None, docker_socket.recv, 4096)
#                 print(f"DATA FROM SOCKET: {data.decode()}")
#                 if not data:
#                     break
#                 await websocket.send_bytes(data)
#             except Exception as e:
#                 print(f"Error reading from Docker socket: {e}")
#                 break

#     async def write_to_socket():
#         """Read data from WebSocket and send it to Docker socket."""
#         while True:
#             try:
#                 # Receive data from WebSocket
#                 message = await websocket.receive()
#                 if "bytes" in message:
#                     print(f"DATA TYPE: {message}")
#                     data = message["bytes"]  # Binary data
#                 elif "text" in message:
#                     print(f"DATA TYPE: {message}")
#                     data = message["text"].encode()  # Text data, encode to bytes
#                 else:
#                     print("Unsupported message type from WebSocket.")
#                     continue
#                 await loop.run_in_executor(None, docker_socket.sendall, data)
#             except WebSocketDisconnect:
#                 print("WebSocket disconnected.")
#                 break
#             except Exception as e:
#                 print(f"Error writing to Docker socket: {e}")
#                 break

#     # Run the tasks concurrently
#     await asyncio.gather(read_from_socket(), write_to_socket())

#     # Cleanup
#     docker_socket.close()


async def proxy_docker_socket(websocket: WebSocket):
    """Handles bidirectional communication between the client and Docker socket."""
    # Create a connection to the Docker Unix socket
    BASE_URL = f"unix:/{DOCKER_SOCKET_PATH}"
    client = docker.DockerClient(base_url=BASE_URL)

    # container_id = 'ecc544955c2a'
    # try:
    #     container: Container = client.containers.get(container_id)
    # except docker.errors.NotFound:
    #     msg = f'Docker container not found:  {container_id}'
    #     await websocket.send_bytes(msg.encode())
    #     await websocket.close()
    #     return

    # container_params = {
    #     'detach': True,
    #     'tty': True,
    #     # 'user': 'root', # should be a variable
    #     # 'hostname': 'webash', # should be a variable
    # }
    # Start the container
    try:
        # Run a container
        container: Container = client.containers.run(
            image="alpine:latest",  # Specify the image
            command="ash",  # Command to run in the container
            stdin_open=True,  # Equivalent to `-i` (interactive)
            tty=True,  # Equivalent to `-t` (allocate a pseudo-TTY)
            detach=True,  # Equivalent to `-d` (run in detached mode)
        )
    except docker.errors.APIError as e:
        print(f"Failed to start container: {e}")
        await websocket.close()
        return

    try:
        # Attach to the container and get the socket
        docker_socket = client.api.attach_socket(
            container=container.id,  # Use the container's ID from the high-level object
            params={
                "stdout": 1,
                "stdin": 1,
                "logs": 1,
                "stream": 1,
            },
            ws=False,  # Set to True for WebSocket connections
        )._sock

    except docker.errors.APIError as e:
        print(f"Failed to attach to container: {e}")
        await websocket.close()
        container.stop()
        container.remove()
        return

    loop = asyncio.get_event_loop()

    async def read_from_socket():
        """Read data from Docker socket and send it to WebSocket."""
        while True:
            try:
                data = await loop.run_in_executor(None, docker_socket.recv, 4096)
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
                msg: str = (
                    await websocket.receive_text()
                )  # Receive data from WebSocket client
                data: bytes = msg.encode()
                # docker_socket.send(data)  # Send data to Docker
                await loop.run_in_executor(None, docker_socket.sendall, data)
            except Exception:
                break

    # Run the tasks concurrently
    try:
        await asyncio.gather(read_from_socket(), write_to_socket())
    finally:
        # Clean up resources
        container.stop()
        container.remove()
        docker_socket.close()
        await websocket.close()
