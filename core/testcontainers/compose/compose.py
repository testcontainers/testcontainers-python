import subprocess
from dataclasses import dataclass, field, fields
from functools import cached_property
from json import loads
from os import PathLike
from typing import List, Optional, Tuple, Union

from typing import TypeVar, Type

_IPT = TypeVar('_IPT')


def _ignore_properties(cls: Type[_IPT], dict_: any) -> _IPT:
    """omits extra fields like @JsonIgnoreProperties(ignoreUnknown = true)

    https://gist.github.com/alexanderankin/2a4549ac03554a31bef6eaaf2eaf7fd5"""
    if isinstance(dict_, cls): return dict_  # noqa
    class_fields = {f.name for f in fields(cls)}
    filtered = {k: v for k, v in dict_.items() if k in class_fields}
    return cls(**filtered)


class ContainerIsNotRunning(RuntimeError):
    pass


class PortIsNotExposed(RuntimeError):
    pass


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
    Publishers: List[PublishedPort] = field(default_factory=list)

    def __post_init__(self):
        if self.Publishers:
            self.Publishers = [
                _ignore_properties(PublishedPort, p) for p in self.Publishers
            ]

    # TODO: you can ask testcontainers.core.docker_client.DockerClient.get_container(self, id: str)
    #       to get you a testcontainer instance which then can stop/restart the instance individually

    def get_publisher(
            self,
            by_port: Optional[int] = None,
            by_host: Optional[str] = None
    ) -> PublishedPort:
        remaining_publishers = self.Publishers

        if by_port:
            remaining_publishers = [
                item for item in remaining_publishers
                if item.TargetPort == by_port
            ]
        if by_host:
            remaining_publishers = [
                item for item in remaining_publishers
                if item.URL == by_host
            ]
        if len(remaining_publishers) == 0:
            raise PortIsNotExposed(
                f"Could not find publisher for for service {self.Service}")
        return remaining_publishers[0]


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
    compose_file_name: Optional[Union[str, List[str]]] = None
    pull: bool = False
    build: bool = False
    wait: bool = True
    env_file: Optional[str] = None
    services: Optional[List[str]] = None

    def __post_init__(self):
        if isinstance(self.compose_file_name, str):
            self.compose_file_name = [self.compose_file_name]

    def __enter__(self) -> "DockerCompose":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    @cached_property
    def docker_compose_command(self) -> List[str]:
        """
        Returns command parts used for the docker compose commands

        Returns:
            cmd: Docker compose command parts.
        """
        docker_compose_cmd = ['docker', 'compose']
        if self.compose_file_name:
            for file in self.compose_file_name:
                docker_compose_cmd += ['-f', file]
        if self.env_file:
            docker_compose_cmd += ['--env-file', self.env_file]
        return docker_compose_cmd

    def start(self) -> None:
        """
        Starts the docker compose environment.
        """
        base_cmd = self.docker_compose_command or []

        # pull means running a separate command before starting
        if self.pull:
            pull_cmd = base_cmd + ['pull']
            self._call_command(cmd=pull_cmd)

        up_cmd = base_cmd + ['up']

        # build means modifying the up command
        if self.build:
            up_cmd.append('--build')

        if self.wait:
            up_cmd.append('--wait')
        else:
            # we run in detached mode instead of blocking
            up_cmd.append('--detach')

        if self.services:
            up_cmd.extend(self.services)

        self._call_command(cmd=up_cmd)

    def stop(self, down=True) -> None:
        """
        Stops the docker compose environment.
        """
        down_cmd = self.docker_compose_command[:]
        if down:
            down_cmd += ['down', '--volumes']
        else:
            down_cmd += ['stop']
        self._call_command(cmd=down_cmd)

    def get_logs(self, *services: str) -> Tuple[str, str]:
        """
        Returns all log output from stdout and stderr of a specific container.

        :param services: which services to get the logs for (or omit, for all)

        Returns:
            stdout: Standard output stream.
            stderr: Standard error stream.
        """
        logs_cmd = self.docker_compose_command + ["logs", *services]

        result = subprocess.run(
            logs_cmd,
            cwd=self.context,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode("utf-8"), result.stderr.decode("utf-8")

    def get_containers(self, include_all=False) -> List[ComposeContainer]:
        """
        Fetch information about running containers via `docker compose ps --format json`.
        Available only in V2 of compose.

        Returns:
            The list of running containers.

        """

        cmd = self.docker_compose_command + ["ps", "--format", "json"]
        if include_all:
            cmd += ["-a"]
        result = subprocess.run(cmd, cwd=self.context, check=True, stdout=subprocess.PIPE)
        stdout = result.stdout.decode("utf-8")
        if not stdout:
            return []
        json_object = loads(stdout)

        if not isinstance(json_object, list):
            return [_ignore_properties(ComposeContainer, json_object)]

        return [
            _ignore_properties(ComposeContainer, item) for item in json_object
        ]

    def get_container(self, service_name: str, include_all=False) -> ComposeContainer:
        matching_containers = [
            item for item in self.get_containers(include_all=include_all)
            if item.Service == service_name
        ]

        if not matching_containers:
            raise ContainerIsNotRunning(
                f"{service_name} is not running in the compose context")

        return matching_containers[0]

    def exec_in_container(
            self,
            service_name: str,
            command: List[str]
    ) -> Tuple[str, str, int]:
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
        exec_cmd = self.docker_compose_command + ['exec', '-T', service_name] + command
        result = subprocess.run(
            exec_cmd,
            cwd=self.context,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return (
            result.stdout.decode("utf-8"),
            result.stderr.decode("utf-8"),
            result.returncode
        )

    def _call_command(self,
                      cmd: Union[str, List[str]],
                      context: Optional[str] = None) -> None:
        context = context or self.context
        subprocess.call(cmd, cwd=context)
