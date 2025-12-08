#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import socket
from typing import Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class ValkeyNotReady(Exception):
    pass


class ValkeyContainer(DockerContainer):
    """
    Valkey container.

    Example:

        .. doctest::

            >>> from testcontainers.valkey import ValkeyContainer

            >>> with ValkeyContainer() as valkey_container:
            ...     connection_url = valkey_container.get_connection_url()
    """

    def __init__(self, image: str = "valkey/valkey:latest", port: int = 6379, **kwargs) -> None:
        super().__init__(image, **kwargs)
        self.port = port
        self.password: Optional[str] = None
        self.with_exposed_ports(self.port)

    def with_password(self, password: str) -> "ValkeyContainer":
        """
        Configure authentication for Valkey.

        Args:
            password: Password for Valkey authentication.

        Returns:
            self: Container instance for method chaining.
        """
        self.password = password
        self.with_command(f"valkey-server --requirepass {password}")
        return self

    def with_image_tag(self, tag: str) -> "ValkeyContainer":
        """
        Specify Valkey version.

        Args:
            tag: Image tag (e.g., '8.0', 'latest', 'bundle:latest').

        Returns:
            self: Container instance for method chaining.
        """
        base_image = self.image.split(":")[0]
        self.image = f"{base_image}:{tag}"
        return self

    def with_bundle(self) -> "ValkeyContainer":
        """
        Enable all modules by switching to valkey-bundle image.

        Returns:
            self: Container instance for method chaining.
        """
        self.image = self.image.replace("valkey/valkey", "valkey/valkey-bundle")
        return self

    def get_connection_url(self) -> str:
        """
        Get connection URL for Valkey.

        Returns:
            url: Connection URL in format valkey://[:password@]host:port
        """
        host = self.get_host()
        port = self.get_exposed_port()
        if self.password:
            return f"valkey://:{self.password}@{host}:{port}"
        return f"valkey://{host}:{port}"

    def get_host(self) -> str:
        """
        Get container host.

        Returns:
            host: Container host IP.
        """
        return self.get_container_host_ip()

    def get_exposed_port(self) -> int:
        """
        Get mapped port.

        Returns:
            port: Exposed port number.
        """
        return int(super().get_exposed_port(self.port))

    @wait_container_is_ready(ValkeyNotReady)
    def _connect(self) -> None:
        """Wait for Valkey to be ready by sending PING command."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.get_host(), self.get_exposed_port()))
            if self.password:
                s.sendall(f"*2\r\n$4\r\nAUTH\r\n${len(self.password)}\r\n{self.password}\r\n".encode())
                auth_response = s.recv(1024)
                if b"+OK" not in auth_response:
                    raise ValkeyNotReady("Authentication failed")
            s.sendall(b"*1\r\n$4\r\nPING\r\n")
            response = s.recv(1024)
            if b"+PONG" not in response:
                raise ValkeyNotReady("Valkey not ready yet")

    def start(self) -> "ValkeyContainer":
        """
        Start the container and wait for it to be ready.

        Returns:
            self: Started container instance.
        """
        super().start()
        self._connect()
        return self
