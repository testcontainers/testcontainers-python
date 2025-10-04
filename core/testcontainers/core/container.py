import contextlib
import sys
from os import PathLike
from socket import socket
from types import TracebackType
from typing import TYPE_CHECKING, Any, Optional, TypedDict, Union, cast

import docker.errors
from docker import version
from docker.models.containers import ExecResult
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
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from testcontainers.core.waiting_utils import WaitStrategy

if TYPE_CHECKING:
    from docker.models.containers import Container

logger = setup_logger(__name__)


class Mount(TypedDict):
    bind: str
    mode: str


class DockerContainer:
    """
    Basic container object to spin up Docker instances.

    Args:
        image: The name of the image to start.
        docker_client_kw: Dictionary with arguments that will be passed to the docker.DockerClient init.
        command: Optional execution command for the container.
        name: Optional name for the container.
        ports: Ports to be exposed by the container. The port number will be automatically assigned on the host, use :code:`get_exposed_port(PORT)` method to get the port number on the host.
        volumes: Volumes to mount into the container. Each entry should be a tuple with three values: host path, container path and mode (default 'ro').
        network: Optional network to connect the container to.
        network_aliases: Optional list of aliases for the container in the network.

    .. doctest::

        >>> from testcontainers.core.container import DockerContainer
        >>> from testcontainers.core.waiting_utils import wait_for_logs

        >>> with DockerContainer("hello-world") as container:
        ...    delay = wait_for_logs(container, "Hello from Docker!")
    """

    def __init__(
        self,
        image: str,
        docker_client_kw: Optional[dict[str, Any]] = None,
        command: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        name: Optional[str] = None,
        ports: Optional[list[int]] = None,
        volumes: Optional[list[tuple[str, str, str]]] = None,
        network: Optional[Network] = None,
        network_aliases: Optional[list[str]] = None,
        _wait_strategy: Optional[WaitStrategy] = None,
        **kwargs: Any,
    ) -> None:
        self.env = env or {}

        self.ports: dict[Union[str, int], Optional[Union[str, int]]] = {}
        if ports:
            self.with_exposed_ports(*ports)

        self.volumes: dict[str, Mount] = {}
        if volumes:
            for vol in volumes:
                self.with_volume_mapping(*vol)

        self.image = image
        self._docker = DockerClient(**(docker_client_kw or {}))
        self._container: Optional[Container] = None
        self._command: Optional[Union[str, list[str]]] = command
        self._name = name
        self._network: Optional[Network] = None
        if network is not None:
            self.with_network(network)

        self._network_aliases: Optional[list[str]] = None
        if network_aliases:
            self.with_network_aliases(*network_aliases)

        self._kwargs = kwargs
        self._wait_strategy: Optional[WaitStrategy] = _wait_strategy

    def with_env(self, key: str, value: str) -> Self:
        self.env[key] = value
        return self

    def with_envs(self, **variables: str) -> Self:
        self.env.update(variables)
        return self

    def with_env_file(self, env_file: Union[str, PathLike[str]]) -> Self:
        env_values = dotenv_values(env_file)
        for key, value in env_values.items():
            assert value is not None
            self.with_env(key, value)
        return self

    def with_bind_ports(self, container: Union[str, int], host: Optional[Union[str, int]] = None) -> Self:
        """
        Bind container port to host port

        :param container: container port
        :param host: host port

        :doctest:

        >>> from testcontainers.core.container import DockerContainer
        >>> container = DockerContainer("nginx")
        >>> container = container.with_bind_ports("8080/tcp", 8080)
        >>> container = container.with_bind_ports("8081/tcp", 8081)

        """
        self.ports[container] = host
        return self

    def with_exposed_ports(self, *ports: Union[str, int]) -> Self:
        """
        Expose ports from the container without binding them to the host.

        :param ports: ports to expose

        :doctest:

        >>> from testcontainers.core.container import DockerContainer
        >>> container = DockerContainer("nginx")
        >>> container = container.with_exposed_ports("8080/tcp", "8081/tcp")

        """

        for port in ports:
            self.ports[port] = None
        return self

    def with_network(self, network: Network) -> Self:
        self._network = network
        return self

    def with_network_aliases(self, *aliases: str) -> Self:
        self._network_aliases = list(aliases)
        return self

    def with_kwargs(self, **kwargs: Any) -> Self:
        self._kwargs = kwargs
        return self

    def maybe_emulate_amd64(self) -> Self:
        if is_arm():
            return self.with_kwargs(platform="linux/amd64")
        return self

    def waiting_for(self, strategy: WaitStrategy) -> Self:
        """Set a wait strategy to be used after container start."""
        self._wait_strategy = strategy
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
            ports=cast("dict[int, Optional[int]]", self.ports),
            name=self._name,
            volumes=self.volumes,
            **{**network_kwargs, **self._kwargs},
        )

        if self._wait_strategy is not None:
            self._wait_strategy.wait_until_ready(self)

        logger.info("Container started: %s", self._container.short_id)
        return self

    def stop(self, force: bool = True, delete_volume: bool = True) -> None:
        if self._container:
            self._container.remove(force=force, v=delete_volume)
        self.get_docker_client().client.close()

    def __enter__(self) -> Self:
        try:
            return self.start()
        except:  # noqa: E722, RUF100
            self.__exit__(*sys.exc_info())
            raise

    def __exit__(
        self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        self.stop()

    def get_container_host_ip(self) -> str:
        connection_mode: ConnectionMode
        connection_mode = self.get_docker_client().get_connection_mode()

        if connection_mode == ConnectionMode.docker_host:
            return self.get_docker_client().host()
        elif connection_mode == ConnectionMode.gateway_ip:
            # mypy:
            container = self._container
            assert container is not None
            return self.get_docker_client().gateway_ip(container.id)
        elif connection_mode == ConnectionMode.bridge_ip:
            # mypy:
            container = self._container
            assert container is not None
            return self.get_docker_client().bridge_ip(container.id)
        else:
            # ensure that we covered all possible connection_modes
            assert_never(connection_mode)

    def get_exposed_port(self, port: int) -> int:
        from testcontainers.core.wait_strategies import ContainerStatusWaitStrategy as C

        C().wait_until_ready(self)
        return self._get_exposed_port(port)

    def _get_exposed_port(self, port: int) -> int:
        if self.get_docker_client().get_connection_mode().use_mapped_port:
            c = self._container
            assert c is not None
            return int(self.get_docker_client().port(c.id, port))
        return port

    def with_command(self, command: Union[str, list[str]]) -> Self:
        self._command = command
        return self

    def with_name(self, name: str) -> Self:
        self._name = name
        return self

    def with_volume_mapping(self, host: Union[str, PathLike[str]], container: str, mode: str = "ro") -> Self:
        mapping: Mount = {"bind": container, "mode": mode}
        self.volumes[str(host)] = mapping
        return self

    def get_wrapped_container(self) -> "Container":
        return self._container

    def get_docker_client(self) -> DockerClient:
        """
        :meta private:
        """
        return self._docker

    def get_logs(self) -> tuple[bytes, bytes]:
        if not self._container:
            raise ContainerStartException("Container should be started before getting logs")
        return self._container.logs(stderr=False), self._container.logs(stdout=False)

    def reload(self) -> None:
        """Reload container information for compatibility with wait strategies."""
        if self._container:
            self._container.reload()

    @property
    def status(self) -> str:
        """Get container status for compatibility with wait strategies."""
        if not self._container:
            return "not_started"
        return cast("str", self._container.status)

    def exec(self, command: Union[str, list[str]]) -> ExecResult:
        if not self._container:
            raise ContainerStartException("Container should be started before executing a command")
        return self._container.exec_run(command)

    def _configure(self) -> None:
        # placeholder if subclasses want to define this and use the default start method
        pass


class Reaper:
    """
    :meta private:
    """

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
        rc = Reaper._container
        assert rc is not None
        rc.waiting_for(LogMessageWaitStrategy(r".* Started!").with_startup_timeout(20))

        container_host = rc.get_container_host_ip()
        container_port = int(rc.get_exposed_port(8080))

        if not container_host or not container_port:
            rcc = rc._container
            assert rcc
            raise ContainerConnectException(
                f"Could not obtain network details for {rcc.id}. Host: {container_host} Port: {container_port}"
            )

        last_connection_exception: Optional[Exception] = None
        for _ in range(50):
            try:
                s = socket()
                Reaper._socket = s
                s.settimeout(1)
                s.connect((container_host, container_port))
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

        rs = Reaper._socket
        assert rs is not None
        rs.send(f"label={LABEL_SESSION_ID}={SESSION_ID}\r\n".encode())

        Reaper._instance = Reaper()

        return Reaper._instance
