from abc import ABC
from typing import Generic, TypeVar, overload

from core.testcontainers.containers.bind_mode import BindMode
from core.testcontainers.containers.selinux_context import SelinuxContext
from testcontainers.containers.wait.strategy.wait_strategy import WaitStrategy

T = TypeVar('T', bound="Container")


class Container(Generic[T], ABC):
    def self(self) -> T:
        return self

    @overload
    def set_command(self, command: str) -> None:
        """Set the command that should be run in the container.

        :param command: a command in single string format (will automatically be split on spaces)
        """
        ...

    @overload
    def set_command(self, command_parts: list[str]) -> None:
        """Set the command that should be run in the container.

        This overload/variant of set_command will use the parts as split.

        :param command_parts: a command as an array of string parts
        """
        ...

    def set_command(self, *args) -> None:
        """Set the command that should be run in the container.

        Consider using `with_command` for building a container in a fluent style.
        """
        ...

    def add_env(self, key: str, value: str) -> None:
        """
        Add an environment variable to be passed to the container.

        Consider using `withEnv` for building a container in a fluent style.

        :param key: environment variable key
        :param value: environment variable value
        """
        ...

    def add_file_system_bind(self, host_path: str, container_path: str, bind_mode: BindMode,
                             selinux_context: SelinuxContext = "SHARED") -> None:
        """
        Adds a file system binding to the container.

        Consider using `with_file_system_bind` for building a container in a fluent style.

        **DEPRECATED** - use `with_copy_to_container` instead.

        :param host_path: the file system path on the host
        :param container_path: the file system path inside the container
        :param bind_mode: the bind mode
        :param selinux_context: selinux context argument to use for this file
        """
        ...

    # links are not supported

    def add_exposed_port(self, port: int) -> None:
        """Add an exposed port.

        Consider using `with_exposed_port` for building a container in a fluent style.

        :param port: the port inside the container to expose
        """

    def add_exposed_ports(self, ports: list[int]) -> None:
        """Add exposed ports.

        Consider using `with_exposed_ports` for building a container in a fluent style.

        :param ports: list of ports to expose
        """

    def waiting_for(self, wait_strategy: WaitStrategy) -> T:
        """Specify the `WaitStrategy` used to determine if the container is ready.

        """
        return self
