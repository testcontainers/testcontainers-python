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

import clickhouse_connect
from clickhouse_connect.driver.exceptions import Error as ClickhouseConnectError
import clickhouse_driver
from clickhouse_driver.errors import Error as ClickhouseDriverError

from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready


class ClickHouseContainer(DbContainer):
    """
    ClickHouse database container. This testcontainer defaults to exposing the TCP port of
    ClickHouse. If you want to use the HTTP interface, specify port 8123 to be exposed.

    Example:

        This example shows how to spin up ClickHouse.
        It demonstrates how to connect to the *TCP* interface using :code:`clickhouse-driver`
        and how to connect to the *HTTP* interface using :code:`clickhouse-connect`, the
        official client library.

        .. doctest::

            >>> from testcontainers.clickhouse import ClickHouseContainer

            >>> # clickhouse_driver is a client lib that uses the TCP interface
            >>> import clickhouse_driver
            >>> # ClickHouseContainer exports the TCP port by default
            >>> with ClickHouseContainer(image="clickhouse/clickhouse-server:21.8") as clickhouse:
            ...     client = clickhouse_driver.Client.from_url(clickhouse.get_connection_url())
            ...     client.execute("select 'working'")
            [('working',)]

            >>> # clickhouse_connect is the official client lib, based on the HTTP interface
            >>> import clickhouse_connect
            >>> # If you want to use the HTTP interface, port 8123 needs to be exposed
            >>> with ClickHouseContainer(port=8123) as clickhouse:
            ...     client = clickhouse_connect.get_client(dsn=clickhouse.get_connection_url())
            ...     client.query("select 'working'").result_rows
            [('working',)]
    """

    def __init__(
        self,
        image: str = "clickhouse/clickhouse-server:latest",
        port: int = 9000,
        username: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        **kwargs
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "user", "username")
        super().__init__(image=image, **kwargs)
        self.username: str = username or os.environ.get("CLICKHOUSE_USER", "test")
        self.password: str = password or os.environ.get("CLICKHOUSE_PASSWORD", "test")
        self.dbname: str = dbname or os.environ.get("CLICKHOUSE_DB", "test")
        self.port = port
        self.with_exposed_ports(self.port)

    @wait_container_is_ready(ClickhouseDriverError, ClickhouseConnectError, EOFError)
    def _connect(self) -> None:
        if self.port == 8123:
            with clickhouse_connect.get_client(dsn=self.get_connection_url()) as client:
                client.command("SELECT version()")
        else:
            with clickhouse_driver.Client.from_url(self.get_connection_url()) as client:
                client.execute("SELECT version()")

    def _configure(self) -> None:
        self.with_env("CLICKHOUSE_USER", self.username)
        self.with_env("CLICKHOUSE_PASSWORD", self.password)
        self.with_env("CLICKHOUSE_DB", self.dbname)

    def get_connection_url(self, host: Optional[str] = None) -> str:
        return self._create_connection_url(
            dialect="clickhouse",
            username=self.username,
            password=self.password,
            dbname=self.dbname,
            host=host,
            port=self.port,
        )
