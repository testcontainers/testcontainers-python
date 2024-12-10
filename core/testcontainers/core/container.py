import contextlib
from os import PathLike
from socket import socket
from typing import TYPE_CHECKING, Optional, Union

import docker.errors
from docker import version
from docker.types import EndpointConfig
from dotenv import dotenv_values
from typing_extensions import Self, assert_never

from testcontainers.core.config import ConnectionMode
from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.exceptions import ContainerConnectException, ContainerStartException
from testcontainers.core.labels import LABEL_SESSION_ID, SESSION_ID
from testcontainers.core.network import Network
from testcontainers.core.utils import is_arm, setup_logger
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs

if TYPE_CHECKING:
    from docker.models.containers import Container

logger = setup_logger(__name__)


class DockerContainer:
    """
    Basic container object to spin up Docker instances.

    .. doctest::

        >>> from testcontainers.core.container import DockerContainer
        >>> from testcontainers.core.waiting_utils import wait_for_logs

        >>> with DockerContainer("hello-world") as container:
        ...    delay = wait_for_logs(container, "Hello from Docker!")
    """

    def __init__(
        self,
        image: str,
        docker_client_kw: Optional[dict] = None,
        **kwargs,
    ) -> None:
        self.env = {}
        self.ports = {}
        self.volumes = {}
        self.image = image
        self._docker = DockerClient(**(docker_client_kw or {}))
        self._container = None
        self._command = None
        self._name = None
        self._network: Optional[Network] = None
        self._network_aliases: Optional[list[str]] = None
        self._kwargs = kwargs

    def with_env(self, key: str, value: str) -> Self:
        self.env[key] = value
        return self

    def with_env_file(self, env_file: Union[str, PathLike]) -> Self:
        env_values = dotenv_values(env_file)
        for key, value in env_values.items():
            self.with_env(key, value)
        return self

    def with_bind_ports(self, container: int, host: Optional[int] = None) -> Self:
        self.ports[container] = host
        return self

    def with_exposed_ports(self, *ports: int) -> Self:
        for port in ports:
            self.ports[port] = None
        return self

    def with_network(self, network: Network) -> Self:
        self._network = network
        return self

    def with_network_aliases(self, *aliases) -> Self:
        self._network_aliases = aliases
        return self

    def with_kwargs(self, **kwargs) -> Self:
        self._kwargs = kwargs
        return self

    def maybe_emulate_amd64(self) -> Self:
        if is_arm():
            return self.with_kwargs(platform="linux/amd64")
        return self

    def start(self) -> Self:
        if not c.ryuk_disabled and self.image != c.ryuk_image:
            logger.debug("Creating Ryuk container")
            Reaper.get_instance()
        logger.info("Pulling image %s", self.image)
        docker_client = self.get_docker_client()
        self._configure()

        network_kwargs = (
            {
                "network": self._network.name,
                "networking_config": {
                    self._network.name: EndpointConfig(version.__version__, aliases=self._network_aliases)
                },
            }
            if self._network
            else {}
        )

        self._container = docker_client.run(
            self.image,
            command=self._command,
            detach=True,
            environment=self.env,
            ports=self.ports,
            name=self._name,
            volumes=self.volumes,
            **network_kwargs,
            **self._kwargs,
        )

        logger.info("Container started: %s", self._container.short_id)
        return self

    def stop(self, force=True, delete_volume=True) -> None:
        if self._container:
            self._container.remove(force=force, v=delete_volume)
        self.get_docker_client().client.close()

    def __enter__(self) -> Self:
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    def get_container_host_ip(self) -> str:
        connection_mode: ConnectionMode
        connection_mode = self.get_docker_client().get_connection_mode()
        if connection_mode == ConnectionMode.docker_host:
            return self.get_docker_client().host()
        elif connection_mode == ConnectionMode.gateway_ip:
            return self.get_docker_client().gateway_ip(self._container.id)
        elif connection_mode == ConnectionMode.bridge_ip:
            return self.get_docker_client().bridge_ip(self._container.id)
        else:
            # ensure that we covered all possible connection_modes
            assert_never(connection_mode)

    @wait_container_is_ready()
    def get_exposed_port(self, port: int) -> int:
        if self.get_docker_client().get_connection_mode().use_mapped_port:
            return self.get_docker_client().port(self._container.id, port)
        return port

    def with_command(self, command: str) -> Self:
        self._command = command
        return self

    def with_name(self, name: str) -> Self:
        self._name = name
        return self

    def with_volume_mapping(self, host: str, container: str, mode: str = "ro") -> Self:
        mapping = {"bind": container, "mode": mode}
        self.volumes[host] = mapping
        return self

    def get_wrapped_container(self) -> "Container":
        return self._container

    def get_docker_client(self) -> DockerClient:
        return self._docker

    def get_logs(self) -> tuple[bytes, bytes]:
        if not self._container:
            raise ContainerStartException("Container should be started before getting logs")
        return self._container.logs(stderr=False), self._container.logs(stdout=False)

    def exec(self, command: Union[str, list[str]]) -> tuple[int, bytes]:
        if not self._container:
            raise ContainerStartException("Container should be started before executing a command")
        return self._container.exec_run(command)

    def _configure(self) -> None:
        # placeholder if subclasses want to define this and use the default start method
        pass


class Reaper:
    _instance: "Optional[Reaper]" = None
    _container: Optional[DockerContainer] = None
    _socket: Optional[socket] = None

    @classmethod
    def get_instance(cls) -> "Reaper":
        if not Reaper._instance:
            Reaper._instance = Reaper._create_instance()

        return Reaper._instance

    @classmethod
    def delete_instance(cls) -> None:
        if Reaper._socket is not None:
            Reaper._socket.close()
            Reaper._socket = None

        if Reaper._container is not None and Reaper._container._container is not None:
            with contextlib.suppress(docker.errors.NotFound):
                Reaper._container.stop()
            Reaper._container = None

        if Reaper._instance is not None:
            Reaper._instance = None

    @classmethod
    def _create_instance(cls) -> "Reaper":
        logger.debug(f"Creating new Reaper for session: {SESSION_ID}")

        Reaper._container = (
            DockerContainer(c.ryuk_image)
            .with_name(f"testcontainers-ryuk-{SESSION_ID}")
            .with_exposed_ports(8080)
            .with_volume_mapping(c.ryuk_docker_socket, "/var/run/docker.sock", "rw")
            .with_kwargs(privileged=c.ryuk_privileged, auto_remove=True)
            .with_env("RYUK_RECONNECTION_TIMEOUT", c.ryuk_reconnection_timeout)
            .start()
        )
        wait_for_logs(Reaper._container, r".* Started!", timeout=20, raise_on_exit=True)

        container_host = Reaper._container.get_container_host_ip()
        container_port = int(Reaper._container.get_exposed_port(8080))

        if not container_host or not container_port:
            raise ContainerConnectException(
                f"Could not obtain network details for {Reaper._container._container.id}. Host: {container_host} Port: {container_port}"
            )

        last_connection_exception: Optional[Exception] = None
        for _ in range(50):
            try:
                Reaper._socket = socket()
                Reaper._socket.settimeout(1)
                Reaper._socket.connect((container_host, container_port))
                last_connection_exception = None
                break
            except (ConnectionRefusedError, OSError) as e:
                if Reaper._socket is not None:
                    with contextlib.suppress(Exception):
                        Reaper._socket.close()
                    Reaper._socket = None
                last_connection_exception = e

                from time import sleep

                sleep(0.5)
        if last_connection_exception:
            raise last_connection_exception

        Reaper._socket.send(f"label={LABEL_SESSION_ID}={SESSION_ID}\r\n".encode())

        Reaper._instance = Reaper()

        return Reaper._instance
