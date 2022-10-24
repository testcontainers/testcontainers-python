"""
Docker Compose Support
======================

Allows to spin up services configured via :code:`docker-compose.yml`.
"""

import requests
import subprocess
from typing import Iterable, List, Optional, Tuple, Union

from testcontainers.core.waiting_utils import wait_container_is_ready
from testcontainers.core.exceptions import ContainerStartException, NoSuchPortExposed


class DockerCompose:
    """
    Manage docker compose environments.

    Args:
        filepath: Relative directory containing the docker compose configuration file.
        compose_file_name: File name of the docker compose configuration file.
        pull: Pull images before launching environment.
        build: Build images referenced in the configuration file.
        env_file: Path to an env file containing environment variables to pass to docker compose.

    Example:

        This example spins up chrome and firefox containers using docker compose.

        .. doctest::

            compose_filename = ["docker-compose-1.yml", "docker-compose-2.yml"]
            with DockerCompose("/home/project", compose_file_name=compose_file_name, pull=True) as \
                    compose:
                host = compose.get_service_host("hub", 4444)
                port = compose.get_service_port("hub", 4444)
                driver = webdriver.Remote(
                    command_executor=("http://{}:{}/wd/hub".format(host,port)),
                    desired_capabilities=CHROME,
                )
                driver.get("http://automation-remarks.com")
                stdout, stderr = compose.get_logs()
                if stderr:
                    print("Errors\\n:{}".format(stderr))

        .. code-block:: yaml

            hub:
            image: selenium/hub
            ports:
            - "4444:4444"
            firefox:
            image: selenium/node-firefox
            links:
                - hub
            expose:
                - "5555"
            chrome:
            image: selenium/node-chrome
            links:
                - hub
            expose:
                - "5555"
    """
    def __init__(
            self,
            filepath: str,
            compose_file_name: Union[str, Iterable] = "docker-compose.yml",
            pull: bool = False,
            build: bool = False,
            env_file: Optional[str] = None) -> None:
        self.filepath = filepath
        self.compose_file_names = [compose_file_name] if isinstance(compose_file_name, str) else \
            list(compose_file_name)
        self.pull = pull
        self.build = build
        self.env_file = env_file

    def __enter__(self) -> "DockerCompose":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    def docker_compose_command(self) -> List[str]:
        """
        Returns command parts used for the docker compose commands

        Returns:
            cmd: Docker compose command parts.
        """
        docker_compose_cmd = ['docker-compose']
        for file in self.compose_file_names:
            docker_compose_cmd += ['-f', file]
        if self.env_file:
            docker_compose_cmd += ['--env-file', self.env_file]
        return docker_compose_cmd

    def start(self) -> None:
        """
        Starts the docker compose environment.
        """
        if self.pull:
            pull_cmd = self.docker_compose_command() + ['pull']
            self._call_command(cmd=pull_cmd)

        up_cmd = self.docker_compose_command() + ['up', '-d']
        if self.build:
            up_cmd.append('--build')

        return_code = self._call_command(cmd=up_cmd)

        if return_code:
            raise ContainerStartException(f"Docker compose failed with return code {return_code}")

    def stop(self) -> None:
        """
        Stops the docker compose environment.
        """
        down_cmd = self.docker_compose_command() + ['down', '-v']
        self._call_command(cmd=down_cmd)

    def get_logs(self) -> Tuple[str, str]:
        """
        Returns all log output from stdout and stderr

        Returns:
            stdout: Standard output stream.
            stderr: Standard error stream.
        """
        logs_cmd = self.docker_compose_command() + ["logs"]
        result = subprocess.run(
            logs_cmd,
            cwd=self.filepath,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout, result.stderr

    def exec_in_container(self, service_name: str, command: List[str]) -> Tuple[str, str]:
        """
        Executes a command in the container of one of the services.

        Args:
            service_name: Name of the docker compose service to run the command in.
        command: Command to execute.

        Returns:
            stdout: Standard output stream.
            stderr: Standard error stream.
        """
        exec_cmd = self.docker_compose_command() + ['exec', '-T', service_name] + command
        result = subprocess.run(
            exec_cmd,
            cwd=self.filepath,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode("utf-8"), result.stderr.decode("utf-8"), result.returncode

    def get_service_port(self, service_name: str, port: int) -> int:
        """
        Returns the mapped port for one of the services.

        Args:
            service_name: Name of the docker compose service.
            port: Internal port to get the mapping for.

        Returns:
            mapped_port: Mapped port on the host.
        """
        return self._get_service_info(service_name, port)[1]

    def get_service_host(self, service_name: str, port: int) -> str:
        """
        Returns the host for one of the services.

        Args:
            service_name: Name of the docker compose service.
            port: Internal port to get the mapping for.

        Returns:
            host: Hostname for the service.
        """
        return self._get_service_info(service_name, port)[0]

    def _get_service_info(self, service: str, port: int) -> List[str]:
        port_cmd = self.docker_compose_command() + ["port", service, str(port)]
        output = subprocess.check_output(port_cmd, cwd=self.filepath).decode("utf-8")
        result = str(output).rstrip().split(":")
        if len(result) != 2 or not all(result):
            raise NoSuchPortExposed(f"port {port} is not exposed for service {service}")
        return result

    def _call_command(self, cmd: Union[str, List[str]], filepath: Optional[str] = None) -> None:
        if filepath is None:
            filepath = self.filepath

        return subprocess.call(cmd, cwd=filepath)


    @wait_container_is_ready(requests.exceptions.ConnectionError)
    def wait_for(self, url: str) -> 'DockerCompose':
        """
        Waits for a response from a given URL. This is typically used to block until a service in
        the environment has started and is responding. Note that it does not assert any sort of
        return code, only check that the connection was successful.

        Args:
            url: URL from one of the services in the environment to use to wait on.
        """
        requests.get(url)
        return self
