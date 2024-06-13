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

import requests

from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class MilvusContainer(DockerContainer):
    """
    Milvus database container.

    Read mode about Milvus: https://milvus.io/docs

    Example:

        The example spins up a Milvus database and connects to it client using MilvisClient.

        .. doctest::

            >>> from testcontainers.milvus import MilvusContainer
            >>> with MilvusContainer("milvusdb/milvus:v2.4.4") as milvus_container:
            ...     milvus_container.get_exposed_port(milvus_container.port) in milvus_container.get_connection_url()
            True
    """

    def __init__(
        self,
        image: str = "milvusdb/milvus:latest",
        port: int = 19530,
        **kwargs,
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.port = port
        self.healthcheck_port = 9091
        self.with_exposed_ports(self.port, self.healthcheck_port)
        self.cmd = "milvus run standalone"

        envs = {"ETCD_USE_EMBED": "true", "ETCD_DATA_DIR": "/var/lib/milvus/etcd", "COMMON_STORAGETYPE": "local"}

        for env, value in envs.items():
            self.with_env(env, value)

    def get_connection_url(self) -> str:
        ip = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"http://{ip}:{port}"

    @wait_container_is_ready()
    def _connect(self) -> None:
        msg = "Welcome to use Milvus!"
        wait_for_logs(self, f".*{msg}.*", c.max_tries, c.sleep_time)
        self._healthcheck()

    def _get_healthcheck_url(self) -> str:
        ip = self.get_container_host_ip()
        port = self.get_exposed_port(self.healthcheck_port)
        return f"http://{ip}:{port}"

    @wait_container_is_ready(requests.exceptions.HTTPError)
    def _healthcheck(self) -> None:
        healthcheck_url = self._get_healthcheck_url()
        response = requests.get(f"{healthcheck_url}/healthz", timeout=1)
        response.raise_for_status()

    def start(self) -> "MilvusContainer":
        """This method starts the Milvus container and runs the healthcheck
        to verify that the container is ready to use."""
        self.with_command(self.cmd)
        super().start()
        self._connect()
        self._healthcheck()
        return self
