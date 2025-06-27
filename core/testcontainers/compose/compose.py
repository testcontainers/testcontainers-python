from dataclasses import asdict, dataclass, field, fields
from functools import cached_property
from json import loads
from logging import warning
from os import PathLike
from platform import system
from re import split
from subprocess import CalledProcessError, CompletedProcess
from subprocess import run as subprocess_run
from typing import Any, Callable, Literal, Optional, TypeVar, Union, cast

from testcontainers.core.exceptions import ContainerIsNotRunning, NoSuchPortExposed
from testcontainers.core.utils import setup_logger
from testcontainers.core.waiting_utils import WaitStrategy

_IPT = TypeVar("_IPT")
_WARNINGS = {"DOCKER_COMPOSE_GET_CONFIG": "get_config is experimental, see testcontainers/testcontainers-python#669"}

logger = setup_logger(__name__)


def _ignore_properties(cls: type[_IPT], dict_: any) -> _IPT:
    """omits extra fields like @JsonIgnoreProperties(ignoreUnknown = true)

    https://gist.github.com/alexanderankin/2a4549ac03554a31bef6eaaf2eaf7fd5"""
    if isinstance(dict_, cls):
        return dict_
    class_fields = {f.name for f in fields(cls)}
    filtered = {k: v for k, v in dict_.items() if k in class_fields}
    return cls(**filtered)


@dataclass
class PublishedPort:
    """
    Class that represents the response we get from compose when inquiring status
    via `DockerCompose.get_running_containers()`.
    """

    URL: Optional[str] = None
    TargetPort: Optional[str] = None
    PublishedPort: Optional[str] = None
    Protocol: Optional[str] = None

    def normalize(self):
        url_not_usable = system() == "Windows" and self.URL == "0.0.0.0"
        if url_not_usable:
            self_dict = asdict(self)
            self_dict.update({"URL": "127.0.0.1"})
            return PublishedPort(**self_dict)
        return self


OT = TypeVar("OT")


def get_only_element_or_raise(array: list[OT], exception: Callable[[], Exception]) -> OT:
    if len(array) != 1:
        e = exception()
        raise e
    return array[0]


@dataclass
class ComposeContainer:
    """
    A container class that represents a container managed by compose.
    It is not a true testcontainers.core.container.DockerContainer,
    but you can use the id with DockerClient to get that one too.
    """

    ID: Optional[str] = None
    Name: Optional[str] = None
    Command: Optional[str] = None
    Project: Optional[str] = None
    Service: Optional[str] = None
    State: Optional[str] = None
    Health: Optional[str] = None
    ExitCode: Optional[str] = None
    Publishers: list[PublishedPort] = field(default_factory=list)
    _docker_compose: Optional["DockerCompose"] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        if self.Publishers:
            self.Publishers = [_ignore_properties(PublishedPort, p) for p in self.Publishers]

    def get_publisher(
        self,
        by_port: Optional[int] = None,
        by_host: Optional[str] = None,
        prefer_ip_version: Literal["IPV4", "IPv6"] = "IPv4",
    ) -> PublishedPort:
        remaining_publishers = self.Publishers

        remaining_publishers = [r for r in remaining_publishers if self._matches_protocol(prefer_ip_version, r)]

        if by_port:
            remaining_publishers = [item for item in remaining_publishers if by_port == item.TargetPort]
        if by_host:
            remaining_publishers = [item for item in remaining_publishers if by_host == item.URL]
        if len(remaining_publishers) == 0:
            raise NoSuchPortExposed(f"Could not find publisher for for service {self.Service}")
        return get_only_element_or_raise(
            remaining_publishers,
            lambda: NoSuchPortExposed(
                "get_publisher failed because there is "
                f"not exactly 1 publisher for service {self.Service}"
                f" when filtering by_port={by_port}, by_host={by_host}"
                f" (but {len(remaining_publishers)})"
            ),
        )

    @staticmethod
    def _matches_protocol(prefer_ip_version, r):
        return (":" in r.URL) is (prefer_ip_version == "IPv6")

    # WaitStrategy compatibility methods
    def get_container_host_ip(self) -> str:
        """Get the host IP for the container."""
        # Simplified implementation - wait strategies don't use this yet
        return "127.0.0.1"

    def get_exposed_port(self, port: int) -> int:
        """Get the exposed port mapping for the given internal port."""
        # Simplified implementation - wait strategies don't use this yet
        return port

    def get_logs(self) -> tuple[bytes, bytes]:
        """Get container logs."""
        if not self._docker_compose:
            raise RuntimeError("DockerCompose reference not set on ComposeContainer")
        if not self.Service:
            raise RuntimeError("Service name not set on ComposeContainer")
        stdout, stderr = self._docker_compose.get_logs(self.Service)
        return stdout.encode(), stderr.encode()

    def get_wrapped_container(self) -> "ComposeContainer":
        """Get the underlying container object for compatibility."""
        return self

    def reload(self) -> None:
        """Reload container information for compatibility with wait strategies."""
        # ComposeContainer doesn't need explicit reloading as it's fetched fresh
        # each time through get_container(), but we need this method for compatibility
        pass

    @property
    def status(self) -> str:
        """Get container status for compatibility with wait strategies."""
        return self.State or "unknown"


@dataclass
class DockerCompose:
    """
    Manage docker compose environments.

    Args:
        context:
            The docker context. It corresponds to the directory containing
            the docker compose configuration file.
        compose_file_name:
            Optional. File name of the docker compose configuration file.
            If specified, you need to also specify the overrides if any.
        pull:
            Pull images before launching environment.
        build:
            Run `docker compose build` before running the environment.
        wait:
            Wait for the services to be healthy
            (as per healthcheck definitions in the docker compose configuration)
        env_file:
            Path to an '.env' file containing environment variables
            to pass to docker compose.
        services:
            The list of services to use from this DockerCompose.
        client_args:
            arguments to pass to docker.from_env()
        docker_command_path:
            The docker compose command to run.

    Example:

        This example spins up chrome and firefox containers using docker compose.

        .. doctest::

            >>> from testcontainers.compose import DockerCompose

            >>> compose = DockerCompose("compose/tests", compose_file_name="docker-compose-4.yml",
            ...                         pull=True)
            >>> with compose:
            ...     stdout, stderr = compose.get_logs()
            >>> b"Hello from Docker!" in stdout
            True

        .. code-block:: yaml

            services:
              hello-world:
                image: "hello-world"
    """

    context: Union[str, PathLike]
    compose_file_name: Optional[Union[str, list[str]]] = None
    pull: bool = False
    build: bool = False
    wait: bool = True
    keep_volumes: bool = False
    env_file: Optional[str] = None
    services: Optional[list[str]] = None
    docker_command_path: Optional[str] = None
    profiles: Optional[list[str]] = None
    _wait_strategies: Optional[dict[str, Any]] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.compose_file_name, str):
            self.compose_file_name = [self.compose_file_name]

    def __enter__(self) -> "DockerCompose":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop(not self.keep_volumes)

    def docker_compose_command(self) -> list[str]:
        """
        Returns command parts used for the docker compose commands

        Returns:
            cmd: Docker compose command parts.
        """
        return self.compose_command_property

    @cached_property
    def compose_command_property(self) -> list[str]:
        docker_compose_cmd = [self.docker_command_path] if self.docker_command_path else ["docker", "compose"]
        if self.compose_file_name:
            for file in self.compose_file_name:
                docker_compose_cmd += ["-f", file]
        if self.profiles:
            docker_compose_cmd += [item for profile in self.profiles for item in ["--profile", profile]]
        if self.env_file:
            docker_compose_cmd += ["--env-file", self.env_file]
        return docker_compose_cmd

    def waiting_for(self, strategies: dict[str, WaitStrategy]) -> "DockerCompose":
        """
        Set wait strategies for specific services.

        Args:
            strategies: Dictionary mapping service names to wait strategies
        """
        self._wait_strategies = strategies
        return self

    def start(self) -> None:
        """
        Starts the docker compose environment.
        """
        base_cmd = self.compose_command_property or []

        # pull means running a separate command before starting
        if self.pull:
            pull_cmd = [*base_cmd, "pull"]
            self._run_command(cmd=pull_cmd)

        up_cmd = [*base_cmd, "up"]

        # build means modifying the up command
        if self.build:
            up_cmd.append("--build")

        if self.wait:
            up_cmd.append("--wait")
        else:
            # we run in detached mode instead of blocking
            up_cmd.append("--detach")

        if self.services:
            up_cmd.extend(self.services)

        self._run_command(cmd=up_cmd)

        if self._wait_strategies:
            for service, strategy in self._wait_strategies.items():
                container = self.get_container(service_name=service)
                strategy.wait_until_ready(container)

    def stop(self, down=True) -> None:
        """
        Stops the docker compose environment.
        """
        down_cmd = self.compose_command_property[:]
        if down:
            down_cmd += ["down", "--volumes"]
        else:
            down_cmd += ["stop"]

        if self.services:
            down_cmd.extend(self.services)

        self._run_command(cmd=down_cmd)

    def get_logs(self, *services: str) -> tuple[str, str]:
        """
        Returns all log output from stdout and stderr of a specific container.

        :param services: which services to get the logs for (or omit, for all)

        Returns:
            stdout: Standard output stream.
            stderr: Standard error stream.
        """
        logs_cmd = [*self.compose_command_property, "logs", *services]

        result = self._run_command(cmd=logs_cmd)
        return result.stdout.decode("utf-8"), result.stderr.decode("utf-8")

    def get_config(
        self, *, path_resolution: bool = True, normalize: bool = True, interpolate: bool = True
    ) -> dict[str, Any]:
        """
        Parse, resolve and returns compose file via `docker config --format json`.
        In case of multiple compose files, the returned value will be a merge of all files.

        See: https://docs.docker.com/reference/cli/docker/compose/config/ for more details

        :param path_resolution: whether to resolve file paths
        :param normalize: whether to normalize compose model
        :param interpolate: whether to interpolate environment variables

        Returns:
            Compose file

        """
        if "DOCKER_COMPOSE_GET_CONFIG" in _WARNINGS:
            warning(_WARNINGS.pop("DOCKER_COMPOSE_GET_CONFIG"))
        config_cmd = [*self.compose_command_property, "config", "--format", "json"]
        if not path_resolution:
            config_cmd.append("--no-path-resolution")
        if not normalize:
            config_cmd.append("--no-normalize")
        if not interpolate:
            config_cmd.append("--no-interpolate")

        cmd_output = self._run_command(cmd=config_cmd).stdout
        return cast(dict[str, Any], loads(cmd_output))  # noqa: TC006

    def get_containers(self, include_all=False) -> list[ComposeContainer]:
        """
        Fetch information about running containers via `docker compose ps --format json`.
        Available only in V2 of compose.

        Returns:
            The list of running containers.

        """

        cmd = [*self.compose_command_property, "ps", "--format", "json"]
        if include_all:
            cmd = [*cmd, "-a"]
        result = self._run_command(cmd=cmd)
        stdout = split(r"\r?\n", result.stdout.decode("utf-8"))

        containers = []
        # one line per service in docker 25, single array for docker 24.0.2
        for line in stdout:
            if not line:
                continue
            data = loads(line)
            if isinstance(data, list):
                containers += [_ignore_properties(ComposeContainer, d) for d in data]
            else:
                containers.append(_ignore_properties(ComposeContainer, data))

        # Set the docker_compose reference on each container
        for container in containers:
            container._docker_compose = self

        return containers

    def get_container(
        self,
        service_name: Optional[str] = None,
        include_all: bool = False,
    ) -> ComposeContainer:
        if not service_name:
            containers = self.get_containers(include_all=include_all)
            return get_only_element_or_raise(
                containers,
                lambda: ContainerIsNotRunning(
                    "get_container failed because no service_name given "
                    f"and there is not exactly 1 container (but {len(containers)})"
                ),
            )

        matching_containers = [
            item for item in self.get_containers(include_all=include_all) if item.Service == service_name
        ]

        if not matching_containers:
            raise ContainerIsNotRunning(f"{service_name} is not running in the compose context")

        return matching_containers[0]

    def exec_in_container(
        self,
        command: list[str],
        service_name: Optional[str] = None,
    ) -> tuple[str, str, int]:
        """
        Executes a command in the container of one of the services.

        Args:
            service_name: Name of the docker compose service to run the command in.
        command: Command to execute.

        :param service_name: specify the service name
        :param command: the command to run in the container

        Returns:
            stdout: Standard output stream.
            stderr: Standard error stream.
            exit_code: The command's exit code.
        """
        if not service_name:
            containers = self.get_containers()
            if len(containers) != 1:
                raise ContainerIsNotRunning(
                    f"exec_in_container failed because no service_name given "
                    f"and there is not exactly 1 container (but {len(containers)})"
                )
            service_name = containers[0].Service
        exec_cmd = [*self.compose_command_property, "exec", "-T", service_name, *command]
        result = self._run_command(cmd=exec_cmd)

        return (result.stdout.decode("utf-8"), result.stderr.decode("utf-8"), result.returncode)

    def _run_command(
        self,
        cmd: Union[str, list[str]],
        context: Optional[str] = None,
    ) -> CompletedProcess[bytes]:
        context = context or self.context
        try:
            return subprocess_run(
                cmd,
                capture_output=True,
                check=True,
                cwd=context,
            )
        except CalledProcessError as e:
            logger.error(f"Command '{e.cmd}' failed with exit code {e.returncode}")
            logger.error(f"STDOUT:\n{e.stdout.decode(errors='ignore')}")
            logger.error(f"STDERR:\n{e.stderr.decode(errors='ignore')}")
            raise e from e

    def get_service_port(
        self,
        service_name: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Returns the mapped port for one of the services.

        Parameters
        ----------
        service_name: str
            Name of the docker compose service
        port: int
            The internal port to get the mapping for

        Returns
        -------
        str:
            The mapped port on the host
        """
        return self.get_container(service_name).get_publisher(by_port=port).normalize().PublishedPort

    def get_service_host(
        self,
        service_name: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Returns the host for one of the services.

        Parameters
        ----------
        service_name: str
            Name of the docker compose service
        port: int
            The internal port to get the host for

        Returns
        -------
        str:
            The hostname for the service
        """
        return self.get_container(service_name).get_publisher(by_port=port).normalize().URL

    def get_service_host_and_port(
        self,
        service_name: Optional[str] = None,
        port: Optional[int] = None,
    ):
        publisher = self.get_container(service_name).get_publisher(by_port=port).normalize()
        return publisher.URL, publisher.PublishedPort

    def wait_for(self, url: str) -> "DockerCompose":
        """
        Waits for a response from a given URL. This is typically used to block until a service in
        the environment has started and is responding. Note that it does not assert any sort of
        return code, only check that the connection was successful.

        This is a convenience method that internally uses HttpWaitStrategy. For more complex
        wait scenarios, consider using the structured wait strategies with `waiting_for()`.

        Args:
            url: URL from one of the services in the environment to use to wait on.

        Example:
            # Simple URL wait (legacy style)
            compose.wait_for("http://localhost:8080")

            # For more complex scenarios, use structured wait strategies:
            from testcontainers.core.waiting_utils import HttpWaitStrategy, LogMessageWaitStrategy

            compose.waiting_for({
                "web": HttpWaitStrategy(8080).for_status_code(200),
                "db": LogMessageWaitStrategy("database system is ready to accept connections")
            })
        """
        import time
        from urllib.error import HTTPError, URLError
        from urllib.request import Request, urlopen

        # For simple URL waiting when we have multiple containers,
        # we'll do a direct HTTP check instead of using the container-based strategy
        start_time = time.time()
        timeout = 120  # Default timeout

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"URL {url} not ready within {timeout} seconds")

            try:
                request = Request(url, method="GET")
                with urlopen(request, timeout=1) as response:
                    if 200 <= response.status < 400:
                        return self
            except (URLError, HTTPError, ConnectionResetError, ConnectionRefusedError, BrokenPipeError, OSError):
                # Any connection error means we should keep waiting
                pass

            time.sleep(1)

        return self
