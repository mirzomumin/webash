import asyncio
import logging
from fastapi import WebSocket
from docker import errors
from docker.models.containers import Container


logger = logging.getLogger("webashapp")


class DockerWebSocketProxy:
    def __init__(self, *, websocket: WebSocket, container: Container):
        self.websocket = websocket
        self.container = container
        self.docker_socket = None

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
                raise

    async def handle_proxy(self):
        """Handle bidirectional communication between WebSocket and Docker socket."""
        try:
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
