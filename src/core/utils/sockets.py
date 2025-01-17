# import asyncio
# import docker
# import docker.errors
# from fastapi import WebSocket
# from docker.models.containers import Container


# DOCKER_SOCKET_PATH = "/var/run/docker.sock"


# async def proxy_docker_socket(websocket: WebSocket):
#     """Handles bidirectional communication between the client and Docker socket."""
#     # Create a connection to the Docker Unix socket
#     BASE_URL = f"unix://{DOCKER_SOCKET_PATH}"
#     client = docker.DockerClient(base_url=BASE_URL)

#     # Start the container
#     try:
#         # Run a container
#         # container: Container = client.containers.run(
#         #     image="alpine:latest",  # Specify the image
#         #     command="ash",  # Command to run in the container
#         #     stdin_open=True,  # Equivalent to `-i` (interactive)
#         #     tty=True,  # Equivalent to `-t` (allocate a pseudo-TTY)
#         #     detach=True,  # Equivalent to `-d` (run in detached mode)
#         # )

#         container: Container = client.containers.get('e6329a9a8cfd')
#         # container.start()
#     except docker.errors.APIError as e:
#         print(f"Failed to start container: {e}")
#         await websocket.close()
#         return

#     try:
#         # Attach to the container and get the socket
#         docker_socket = container.attach_socket(
#             params={
#                 "stdout": 1,
#                 "stdin": 1,
#                 "logs": 1,
#                 "stream": 1,
#             },
#             ws=False,
#         )._sock

#     except docker.errors.APIError as e:
#         print(f"Failed to attach to container: {e}")
#         await websocket.close()
#         container.stop()
#         return

#     loop = asyncio.get_event_loop()

#     async def read_from_socket():
#         """Read data from Docker socket and send it to WebSocket."""
#         while True:
#             try:
#                 data = await loop.run_in_executor(None, docker_socket.recv, 4096)
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
#                 msg: str = (
#                     await websocket.receive_text()
#                 )  # Receive data from WebSocket client
#                 data: bytes = msg.encode()
#                 await loop.run_in_executor(None, docker_socket.sendall, data)
#             except Exception as e:
#                 print(f"Error writing to Docker socket: {e}")
#                 break

#     # Run the tasks concurrently
#     try:
#         await asyncio.gather(read_from_socket(), write_to_socket())
#     finally:
#         # Clean up resources
#         container.stop()
#         # container.remove()
#         docker_socket.close()
#         await websocket.close()


import asyncio
from fastapi import WebSocket
import docker
from docker.models.containers import Container

DOCKER_SOCKET_PATH = "/var/run/docker.sock"


class DockerWebSocketProxy:
    def __init__(self, websocket: WebSocket, container_id: str = None):
        self.websocket = websocket
        self.container_id = container_id
        self.client = docker.DockerClient(base_url=f"unix://{DOCKER_SOCKET_PATH}")
        self.container = None
        self.docker_socket = None

    async def connect_to_container(self):
        """Connect to the specified Docker container."""
        try:
            # Run a container
            self.container: Container = self.client.containers.run(
                image="alpine:latest",  # Specify the image
                command="ash",  # Command to run in the container
                stdin_open=True,  # Equivalent to `-i` (interactive)
                tty=True,  # Equivalent to `-t` (allocate a pseudo-TTY)
                detach=True,  # Equivalent to `-d` (run in detached mode)
            )
            # self.container = self.client.containers.get(self.container_id)
            # self.container.start()
        except docker.errors.NotFound:
            print(f"Container {self.container_id} not found.")
            raise
        except docker.errors.APIError as e:
            print(f"Docker API error: {e}")
            raise

    def attach_to_socket(self):
        """Attach to the Docker container's socket."""
        try:
            self.docker_socket = self.container.attach_socket(
                params={
                    "stdout": 1,
                    "stdin": 1,
                    "logs": 1,
                    "stream": 1,
                },
                ws=False,
            )._sock
        except docker.errors.APIError as e:
            print(f"Failed to attach to container: {e}")
            self.cleanup()
            raise

    async def read_from_socket(self):
        """Read data from Docker socket and send it to WebSocket."""
        loop = asyncio.get_event_loop()
        while True:
            try:
                data = await loop.run_in_executor(None, self.docker_socket.recv, 4096)
                if not data:
                    break
                await self.websocket.send_bytes(data)
            except Exception as e:
                print(f"Error reading from Docker socket: {e}")
                raise

    async def write_to_socket(self):
        """Read data from WebSocket and send it to Docker socket."""
        loop = asyncio.get_event_loop()
        while True:
            try:
                msg = await self.websocket.receive_text()
                data = msg.encode()
                await loop.run_in_executor(None, self.docker_socket.sendall, data)
            except Exception as e:
                print(f"Error writing to Docker socket: {e}")
                raise

    async def handle_proxy(self):
        """Handle bidirectional communication between WebSocket and Docker socket."""
        try:
            await self.connect_to_container()
            self.attach_to_socket()
            await asyncio.gather(self.read_from_socket(), self.write_to_socket())
        except Exception as e:
            print(f"Exception: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        if self.container:
            try:
                # self.container.stop(timeout=0)
                self.container.remove(force=True)
            except docker.errors.APIError as e:
                print(f"Error stopping container: {e}")
        if self.docker_socket:
            self.docker_socket.close()
