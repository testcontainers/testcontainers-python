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
import random
import socket
import string
from typing import Any, Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class SocatContainer(DockerContainer):
    """
    A container that uses socat to forward TCP connections.
    """

    def __init__(
        self,
        image: str = "alpine/socat:1.7.4.3-r0",
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new SocatContainer with the given image.

        Args:
            image: The Docker image to use. Defaults to "alpine/socat:1.7.4.3-r0".
            **kwargs: Additional keyword arguments to pass to the DockerContainer constructor.
        """
        # Dictionary to store targets (port -> host:port mappings)
        self.targets: dict[int, str] = {}

        kwargs["entrypoint"] = "/bin/sh"

        random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.with_name(f"testcontainers-socat-{random_suffix}")

        super().__init__(image=image, **kwargs)

    def with_target(self, exposed_port: int, host: str, internal_port: Optional[int] = None) -> "SocatContainer":
        """
        Add a target to forward connections from the exposed port to the given host and port.

        Args:
            exposed_port: The port to expose on the container.
            host: The host to forward connections to.
            internal_port: The port on the host to forward connections to. Defaults to the exposed_port if not provided.

        Returns:
            Self: The container instance for chaining.
        """
        if internal_port is None:
            internal_port = exposed_port

        self.with_exposed_ports(exposed_port)
        self.targets[exposed_port] = f"{host}:{internal_port}"
        return self

    def _configure(self) -> None:
        if not self.targets:
            return

        socat_commands = []
        for port, target in self.targets.items():
            socat_commands.append(f"socat TCP-LISTEN:{port},fork,reuseaddr TCP:{target}")

        command = " & ".join(socat_commands)

        self.with_command(f'-c "{command}"')

    def start(self) -> "SocatContainer":
        super().start()
        self._connect()
        return self

    @wait_container_is_ready(OSError)
    def _connect(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            next_port = next(iter(self.ports))
            # todo remove this limitation
            assert isinstance(next_port, int)
            s.connect((self.get_container_host_ip(), int(self.get_exposed_port(next_port))))
