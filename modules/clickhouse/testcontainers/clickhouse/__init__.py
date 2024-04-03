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
import os
from typing import Optional
from urllib.error import URLError
from urllib.request import urlopen

from typing_extensions import override

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import create_connection_string, raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready


class ClickHouseContainer(DockerContainer):
    """
    ClickHouse database container.

    Example:

        The example spins up a ClickHouse database and connects to it using the
        :code:`clickhouse-driver`.

        .. doctest::

            >>> from clickhouse_driver import Client
            >>> from testcontainers.clickhouse import ClickHouseContainer

            >>> with ClickHouseContainer("clickhouse/clickhouse-server:24.3.1") as clickhouse:
            ...     client = Client.from_url(clickhouse.get_connection_url())
            ...     client.execute("select 'working'")
            [('working',)]
    """

    def __init__(
        self,
        image: str = "clickhouse/clickhouse-server:latest",
        port: int = 9000,
        username: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        **kwargs,
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "user", "username")
        super().__init__(image=image, **kwargs)
        self.username = username or os.environ.get("CLICKHOUSE_USER", "test")
        self.password = password or os.environ.get("CLICKHOUSE_PASSWORD", "test")
        self.dbname = dbname or os.environ.get("CLICKHOUSE_DB", "test")
        self.port = port
        self.with_exposed_ports(self.port)
        self.with_exposed_ports(8123)

    @override
    @wait_container_is_ready(URLError)
    def _wait_until_ready(self) -> None:
        with urlopen(f"http://{self.get_container_host_ip()}:{self.get_exposed_port(8123)}") as r:
            assert b"Ok" in r.read()

    @override
    def _configure(self) -> None:
        self.with_env("CLICKHOUSE_USER", self.username)
        self.with_env("CLICKHOUSE_PASSWORD", self.password)
        self.with_env("CLICKHOUSE_DB", self.dbname)

    def get_connection_url(self) -> str:
        return create_connection_string(
            dialect="clickhouse",
            username=self.username,
            password=self.password,
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(8123),
            dbname=self.dbname,
        )
