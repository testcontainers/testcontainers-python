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

from testcontainers.core.generic import DockerContainer
from testcontainers.core.wait_strategies import CompositeWaitStrategy, HttpWaitStrategy, LogMessageWaitStrategy


class MilvusContainer(DockerContainer):
    """
    Milvus database container.

    Read mode about Milvus: https://milvus.io/docs

    Example:

        The example spins up a Milvus database and connects to it client using MilvisClient.

        .. doctest::

            >>> from testcontainers.community.milvus import MilvusContainer
            >>> with MilvusContainer("milvusdb/milvus:v2.4.4") as milvus_container:
            ...     str(milvus_container.get_exposed_port(milvus_container.port)) in milvus_container.get_connection_url()
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
        self.with_command("milvus run standalone")

        self.with_env("ETCD_USE_EMBED", "true")
        self.with_env("ETCD_DATA_DIR", "/var/lib/milvus/etcd")
        self.with_env("COMMON_STORAGETYPE", "local")

        self.waiting_for(
            CompositeWaitStrategy(
                LogMessageWaitStrategy("Welcome to use Milvus!"),
                HttpWaitStrategy(self.healthcheck_port, "/healthz"),
            )
        )

    def get_connection_url(self) -> str:
        ip = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"http://{ip}:{port}"
