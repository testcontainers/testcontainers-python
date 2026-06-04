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
import uuid
from types import TracebackType
from typing import TYPE_CHECKING, Any, Optional

from testcontainers.core.docker_client import DockerClient

if TYPE_CHECKING:
    from docker.models.networks import Network as DockerNetwork


class Network:
    """
    Network context manager for programmatically connecting containers.
    """

    def __init__(
        self, docker_client_kw: Optional[dict[str, Any]] = None, docker_network_kw: Optional[dict[str, Any]] = None
    ):
        self.name = str(uuid.uuid4())
        self._docker = DockerClient(**(docker_client_kw or {}))
        self._docker_network_kw = docker_network_kw or {}
        self._network: Optional[DockerNetwork] = None

    @property
    def _unwrap_network(self) -> "DockerNetwork":
        s_n = self._network
        assert s_n is not None
        return s_n

    @property
    def id(self) -> Optional[str]:
        network_id = self._unwrap_network.id
        if isinstance(network_id, str):
            return network_id
        return None

    def connect(self, container_id: str, network_aliases: Optional[list[str]] = None) -> None:
        self._unwrap_network.connect(container_id, aliases=network_aliases)

    def remove(self) -> None:
        self._unwrap_network.remove()

    def create(self) -> "Network":
        self._network = self._docker.client_networks_create(self.name, self._docker_network_kw)
        return self

    def __enter__(self) -> "Network":
        return self.create()

    def __exit__(
        self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        self.remove()
