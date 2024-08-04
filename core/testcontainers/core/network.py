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
from typing import Optional

from testcontainers.core.docker_client import DockerClient


class Network:
    """
    Network context manager for programmatically connecting containers.
    """

    def __init__(self, docker_client_kw: Optional[dict] = None, docker_network_kw: Optional[dict] = None) -> None:
        self.name = str(uuid.uuid4())
        self._docker = DockerClient(**(docker_client_kw or {}))
        self._docker_network_kw = docker_network_kw or {}

    def connect(self, container_id: str, network_aliases: Optional[list] = None):
        self._network.connect(container_id, aliases=network_aliases)

    def remove(self) -> None:
        self._network.remove()

    def create(self) -> "Network":
        self._network = self._docker.client_networks_create(self.name, self._docker_network_kw)
        self.id = self._network.id
        return self

    def __enter__(self) -> "Network":
        return self.create()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.remove()
