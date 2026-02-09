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

from typing import Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import ExecWaitStrategy


class ValkeyContainer(DockerContainer):
    """
    Valkey container.

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
        self.with_command(["valkey-server", "--requirepass", password])
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

    def start(self) -> "ValkeyContainer":
        """
        Start the container and wait for it to be ready.

        Returns:
            self: Started container instance.
        """
        if self.password:
            self.waiting_for(ExecWaitStrategy(["valkey-cli", "-a", self.password, "ping"]))
        else:
            self.waiting_for(ExecWaitStrategy(["valkey-cli", "ping"]))

        super().start()
        return self
