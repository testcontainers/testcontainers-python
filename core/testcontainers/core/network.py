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

from testcontainers.core.docker_client import DockerClient


class Network(object):
    """
    Network context manager to conveniently connect containers.
    """

    def __init__(self, name, docker_client_kw: Optional[dict] = None, **kwargs) -> None:
        self.name = name
        self._docker = DockerClient(**(docker_client_kw or {}))
        self._kwargs = kwargs

    def remove(self) -> None:
        self._network.remove()

    def __enter__(self) -> 'Network':
        self._network = self._docker.client.networks.create(self.name, **self._kwargs)
        self.id = self._network.id
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.remove()

    def __del__(self) -> None:
        if self._network is not None:
            try:
                self.remove()
            except:  # noqa: E722
                pass
