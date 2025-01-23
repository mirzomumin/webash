import logging
import asyncio
from fastapi import WebSocket
from docker import DockerClient, errors
from docker.models.containers import Container
from src.core.models.user import User


logger = logging.getLogger("webashapp")


class DockerWebSocketProxy:
    def __init__(self, websocket: WebSocket, client: DockerClient, user: User):
        self.websocket = websocket
        self.client = client
        self.user = user
        self.container = None
        self.docker_socket = None

    async def connect_to_container(self):
        """Connect to the Docker container."""
        try:
            username = self.user.username or self.user.first_name or self.user.last_name
            home_dir = f"/home/{username}"
            colored_ps1 = (
                "\\[\\e[1;32m\\]\\u@\\h\\[\\e[0m\\]:\\[\\e[1;34m\\]\\w\\[\\e[0m\\]\\$ "
            )

            # Run a container
            self.container: Container = self.client.containers.run(
                image="alpine:latest",  # Specify the image
                command="ash",  # Command to run in the container
                stdin_open=True,  # Equivalent to `-i` (interactive)
                tty=True,  # Equivalent to `-t` (allocate a pseudo-TTY)
                detach=True,  # Equivalent to `-d` (run in detached mode)
                environment={
                    "PS1": colored_ps1  # Custom PS1 environment variable
                },
                hostname="webash",
                entrypoint=f"sh -c 'adduser -D {username} && su {username} -c ash'",
                working_dir=home_dir,
                healthcheck={
                    "test": ["CMD-SHELL", "getent hosts $(hostname) || exit 1"],
                    "interval": 5000000,
                    "timeout": 5000000,
                    "retries": 0,
                    "start_period": 0,
                },
            )

            # for further release
            # self.container = self.client.containers.get(self.container_id)
            # self.container.start()
        except errors.NotFound:
            logger.error(f"Container {self.container.id} not found.")
            raise
        except errors.APIError as e:
            logger.error(f"Docker API error: {e}")
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

        except errors.APIError as e:
            logger.error(f"Failed to attach to container: {e}")
            self.cleanup()
            raise

    async def read_from_socket(self):
        loop = asyncio.get_event_loop()
        while True:
            try:
                data = await loop.run_in_executor(None, self.docker_socket.recv, 4096)
                if not data:
                    break
                await self.websocket.send_bytes(data)
            except Exception as e:
                logger.error(f"Error reading from Docker socket: {e}")
                raise

    async def write_to_socket(self):
        loop = asyncio.get_event_loop()
        while True:
            try:
                msg = await self.websocket.receive_text()
                data = msg.encode()
                await loop.run_in_executor(None, self.docker_socket.sendall, data)
            except Exception as e:
                logger.error(f"Error writing to Docker socket: {e}")
                raise

    async def monitor_container_state(self):
        while True:
            try:
                if not self.is_container_running():
                    logger.info("Container stopped or removed. Closing WebSocket.")
                    await self.websocket.close(code=1001, reason="Container stopped")
                    break
                await asyncio.sleep(5)  # Check state every 5 seconds
            except Exception as e:
                logger.error(f"Error monitoring container state: {e}")
                break

    async def handle_proxy(self):
        """Handle bidirectional communication between WebSocket and Docker socket."""
        try:
            await self.connect_to_container()
            self.attach_to_socket()
            await asyncio.gather(
                self.read_from_socket(),
                self.write_to_socket(),
                self.monitor_container_state(),
            )
        except Exception as e:
            logger.error(f"Exception: {e}")
            raise
        finally:
            self.cleanup()

    def is_container_running(self) -> bool:
        """Check if the container is running."""
        try:
            self.container.reload()  # Reload container attributes
            state = self.container.attrs.get("State", {})
            return state.get("Running", False)  # Return True if running
        except errors.APIError as e:
            logger.error(f"Error checking container state: {e}")
            return False

    def cleanup(self):
        """Clean up resources."""
        if self.container:
            try:
                self.container.remove(force=True)
                # for further release
                # self.container.stop(timeout=0)
                #
            except errors.APIError as e:
                logger.error(f"Error stopping container: {e}")
        if self.docker_socket:
            self.docker_socket.close()
