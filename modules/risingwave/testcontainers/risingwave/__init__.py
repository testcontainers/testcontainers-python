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

from __future__ import annotations

from risingwave.core import RisingWave, RisingWaveConnOptions
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import (
    wait_container_is_ready,
    wait_for_logs,
)


class RisingWaveContainer(DockerContainer):
    """
    RisingWave database container.

    Example:

        The example spins up a RisingWave database and connects to it using
        the :code:`risingwave-py` library.

        .. doctest::

            >>> from testcontainers.risingwave import RisingWaveContainer

            >>> with RisingWaveContainer("risingwavelabs/risingwave:v2.0.2") as rw:
            ...     client = rw.get_client()
            ...     version = client.fetchone("select version()")
            >>> version
            'PostgreSQL 13.14.0-RisingWave-2.0.2...'
    """

    _DEFAULT_PORT = 4566

    def __init__(
        self,
        image: str = "risingwavelabs/risingwave:latest",
        port: int = _DEFAULT_PORT,  # external port
        internal_port: int = _DEFAULT_PORT,
        username: str = "root",
        password: str = "",
        dbname: str = "dev",
        **kwargs,
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.username: str = username
        self.password: str = password
        self.dbname: str = dbname
        # support concurrent testing by using different ports
        self.internal_port: int = internal_port
        self.port: int = port

        self.with_exposed_ports(self.internal_port)
        self.with_bind_ports(self.internal_port, self.port)

    def _configure(self) -> None:
        self.with_command("single_node")

    @wait_container_is_ready()
    def _connect(self) -> None:
        wait_for_logs(self, predicate="RisingWave standalone mode is ready")

    def get_client(self, **kwargs) -> RisingWave:
        conn = RisingWaveConnOptions.from_connection_info(
            host=kwargs.get("host", self.get_container_host_ip()),
            user=kwargs.get("user", self.username),
            password=kwargs.get("password", self.password),
            port=kwargs.get("port", self.port),
            database=kwargs.get("database", self.dbname),
        )
        return RisingWave(conn)

    def start(self) -> RisingWaveContainer:
        super().start()
        self._connect()
        return self
