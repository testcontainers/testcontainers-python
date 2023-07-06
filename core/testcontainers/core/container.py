from docker.models.containers import Container
import os
from typing import Iterable, Optional, Tuple

from .waiting_utils import wait_container_is_ready
from .docker_client import DockerClient
from .exceptions import ContainerStartException
from .utils import setup_logger, inside_container, is_arm

logger = setup_logger(__name__)


class DockerContainer:
    """Basic container object to spin up Docker instances.

    .. doctest::

        >>> from testcontainers.core.container import DockerContainer
        >>> from testcontainers.core.waiting_utils import wait_for_logs

        >>> with DockerContainer("hello-world") as container:
        ...    delay = wait_for_logs(container, "Hello from Docker!")

    """

    def __init__(
        self, image: str, docker_client_kw: Optional[dict] = None, **kwargs
    ) -> None:
        self.env = {}
        self.ports = {}
        self.volumes = {}
        self.image = image
        self._docker = DockerClient(**(docker_client_kw or {}))
        self._container = None
        self._command = None
        self._name = None
        self._kwargs = kwargs

    def with_env(self, key: str, value: str) -> "DockerContainer":
        """Set the environment variable. DockerContainer object stores variables as a dictionary.

        Args:
            key (str): The environment variable key.
            value (str): The environment variable value.
        Returns:
            DockerContainer: The DockerContainer object with the added environment variable.
        """
        self.env[key] = value
        return self

    def with_bind_ports(self, container: int, host: int = None) -> "DockerContainer":
        """Set port binding for a container.

        Args:
            container (int): Port exposed inside the container.
            host (int): Port exposed on the host.
        Returns:
            DockerContainer: The DockerContainer object with the specified bind ports.
        """
        self.ports[container] = host
        return self

    def with_exposed_ports(self, *ports: Iterable[int]) -> "DockerContainer":
        """Set exposed ports for a container. The host is assigned a random port.

        Args:
            container (Iterable[int]): List of exposed ports.
        Returns:
            DockerContainer: The DockerContainer object with the specified exposed ports.
        """
        for port in ports:
            self.ports[port] = None
        return self

    def with_kwargs(self, **kwargs) -> "DockerContainer":
        """Set keyword arguments for a wrapped container.

        Args:
            **kwargs: Arbitrary keyword arguments.
        Returns:
            DockerContainer: The DockerContainer object with the specified keyword arguments.
        """
        self._kwargs = kwargs
        return self

    def maybe_emulate_amd64(self) -> "DockerContainer":
        """Set platform to linux/amd64.

        Returns:
            DockerContainer: The DockerContainer with the specified platform.
        """
        if is_arm():
            return self.with_kwargs(platform="linux/amd64")
        return self

    def start(self) -> "DockerContainer":
        """Run a container. By default, containers are run in a background.

        Returns:
            DockerContainer: The DockerContainer object with the wrapped running container.
        """
        logger.info("Pulling image %s", self.image)
        docker_client = self.get_docker_client()
        self._container = docker_client.run(
            self.image,
            command=self._command,
            detach=True,
            environment=self.env,
            ports=self.ports,
            name=self._name,
            volumes=self.volumes,
            **self._kwargs
        )
        logger.info("Container started: %s", self._container.short_id)
        return self

    def stop(self, force=True, delete_volume=True) -> None:
        """Stop and remove container.

        Arguments:
            force (bool): Force the removal of the running container.
            delete_volume (bool): Remove the volume associated with the container.
        """
        self.get_wrapped_container().remove(force=force, v=delete_volume)

    def __enter__(self) -> "DockerContainer":
        """Start the wrapped container.

        Returns:
            DockerContainer: The DockerContainer object with the wrapped running container.
        """
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop the container."""
        self.stop()

    def __del__(self) -> None:
        """Try to remove the container in all circumstances."""
        if self._container is not None:
            try:
                self.stop()
            except:  # noqa: E722
                pass

    def get_container_host_ip(self) -> str:
        """Get the container host IP.

        Returns:
            str: The hostname or IP address of the Docker host.
        """
        # infer from docker host
        host = self.get_docker_client().host()
        if not host:
            return "localhost"

        # check testcontainers itself runs inside docker container
        if inside_container() and not os.getenv("DOCKER_HOST"):
            # If newly spawned container's gateway IP address from the docker
            # "bridge" network is equal to detected host address, we should use
            # container IP address, otherwise fall back to detected host
            # address. Even it's inside container, we need to double check,
            # because docker host might be set to docker:dind, usually in CI/CD environment
            gateway_ip = self.get_docker_client().gateway_ip(self._container.id)

            if gateway_ip == host:
                return self.get_docker_client().bridge_ip(self._container.id)
            return gateway_ip
        return host

    @wait_container_is_ready()
    def get_exposed_port(self, port: int) -> str:
        """Return the exposed port from the container.

        Arguments:
            port (int): Port on the host machine.
        Returns:
            str: The Container's exposed port.
        """
        mapped_port = self.get_docker_client().port(self._container.id, port)
        if inside_container():
            gateway_ip = self.get_docker_client().gateway_ip(self._container.id)
            host = self.get_docker_client().host()

            if gateway_ip == host:
                return port
        return mapped_port

    def with_command(self, command: str) -> "DockerContainer":
        """Set the command to be run in the container.

        Arguments:
            command (str): The command to be run in the container.
        Returns:
            DockerContainer: The DockerContainer object with the set command attribute.
        """
        self._command = command
        return self

    def with_name(self, name: str) -> "DockerContainer":
        """Set the name for the container.

        Arguments:
            name (str): The name for the container.
        Returns:
            DockerContainer: The DockerContainer object with the set name attribute.
        """
        self._name = name
        return self

    def with_volume_mapping(
        self, host: str, container: str, mode: str = "ro"
    ) -> "DockerContainer":
        """Set the volume mapping for the container.

        Arguments:
            host (str): The host path or a volume name.
            container (str): The path to mount the volume inside the container.
            mode (str): Either "rw" to mount the volume read/write, or "ro" to mount it read-only.
        Returns:
            DockerContainer: The DockerContainer object with set volume mapping.
        """
        mapping = {"bind": container, "mode": mode}
        self.volumes[host] = mapping
        return self

    def get_wrapped_container(self) -> Container:
        """Return the wrapped container object.

        Returns:
            Container: The Container object representing the wrapped container.
        """
        return self._container

    def get_docker_client(self) -> DockerClient:
        """Get the Docker client object.

        Returns:
            DockerClient: The DockerClient object.
        """
        return self._docker

    def get_logs(self) -> Tuple[str, str]:
        """Return logs from the wrapped container.

        Returns:
            Tuple[str, str]: The tuple representing stdout and stderr pair.
        Raises:
            ContainerStartException: Raised in the case when the container is not started.
        """
        if not self._container:
            raise ContainerStartException(
                "Container should be started before getting logs"
            )
        return self._container.logs(stderr=False), self._container.logs(stdout=False)

    def exec(self, command) -> Tuple[int, str]:
        """Run the command in the container.

        Returns:
            Tuple[int, str]: The tuple representing the exit_code and output.
        Raises:
            ContainerStartException: Raised in the case when the container is not started.
        """
        if not self._container:
            raise ContainerStartException(
                "Container should be started before executing a command"
            )
        return self.get_wrapped_container().exec_run(command)
