import logging
from uuid import UUID
from docker import DockerClient, errors
from docker.models.containers import Container
from src.core.models.user import User


logger = logging.getLogger("webashapp")


class ContainerManager:
    """Docker containers manager"""

    def __init__(self):
        self.containers: dict[UUID, Container] = {}

    def add(self, *, user_id: UUID, container: Container) -> None:
        self.containers[user_id] = container

    def create(self, *, user: User, docker_client: DockerClient):
        """Create and run a Docker container."""

        try:
            username = user.username or user.first_name or user.last_name
            home_dir = f"/home/{username}"
            colored_ps1 = (
                "\\[\\e[1;32m\\]\\u@\\h\\[\\e[0m\\]:\\[\\e[1;34m\\]\\w\\[\\e[0m\\]\\$ "
            )

            # Create a Docker volume with a size limit of 50 MB
            # volume = docker_client.volumes.create(
            #     name=username,
            #     driver="local",
            #     driver_opts={"type": "tmpfs", "device": "tmpfs", "o": "size=50m"}
            # )

            container: Container = docker_client.containers.run(
                image="debian:12.1",
                command="/bin/bash",
                stdin_open=True,
                tty=True,
                detach=True,
                environment={"PS1": colored_ps1},
                hostname="webash",
                entrypoint=f"sh -c 'adduser -D {username} && su {username} -c sh'",
                working_dir=home_dir,
                healthcheck={
                    "test": ["CMD-SHELL", "getent hosts $(hostname) || exit 1"],
                    "interval": 5000000,
                    "timeout": 5000000,
                    "retries": 0,
                    "start_period": 0,
                },
                nano_cpus=100_000_000,  # 0.1 CPU
                # cpu_period=100_000,  # Required for cpu_quota to work
                # cpu_quota=10_000,  # 0.1 CPU (10000 microseconds per 100000)
                mem_limit=20 * 1024 * 1024,  # 10 MB
                cpuset_cpus="0",
                # volumes={volume.name: {"bind": home_dir, "mode": "rw"}}
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

        self.containers[user.id] = container
        return container

    def get_container(self, *, user_id: UUID) -> Container | None:
        return self.containers.get(user_id)

    def remove(self, *, user_id: UUID) -> None:
        container = self.get_container(user_id=user_id)
        try:
            container.remove(force=True)
            # for further release
            # container.stop(timeout=0)

        except errors.APIError as e:
            logger.error(f"Error stopping container: {e}")
        del self.containers[user_id]


manager = ContainerManager()
