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

import clickhouse_driver
from clickhouse_driver.errors import Error

from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class ClickHouseContainer(DbContainer):
    """
    ClickHouse database container.

    Example
    -------
    The example spins up a ClickHouse database and connects to it
    using the :code:`clickhouse-driver`.

    .. doctest::

        >>> import clickhouse_driver
        >>> from testcontainers.clickhouse import ClickHouseContainer

        >>> with ClickHouseContainer("clickhouse/clickhouse-server:21.8") as clickhouse:
        ...     client = clickhouse_driver.Client.from_url(clickhouse.get_connection_url())
        ...     client.execute("select 'working'")
        [('working',)]
    """

    CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "test")
    CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "test")
    CLICKHOUSE_DB = os.environ.get("CLICKHOUSE_DB", "test")

    def __init__(
            self,
            image="clickhouse/clickhouse-server:latest",
            port=9000,
            user=None,
            password=None,
            dbname=None
    ):
        super().__init__(image=image)

        self.CLICKHOUSE_USER = user or self.CLICKHOUSE_USER
        self.CLICKHOUSE_PASSWORD = password or self.CLICKHOUSE_PASSWORD
        self.CLICKHOUSE_DB = dbname or self.CLICKHOUSE_DB
        self.port_to_expose = port
        self.with_exposed_ports(self.port_to_expose)

    @wait_container_is_ready(Error, EOFError)
    def _connect(self):
        with clickhouse_driver.Client.from_url(self.get_connection_url()) as client:
            client.execute("SELECT version()")

    def _configure(self):
        self.with_env("CLICKHOUSE_USER", self.CLICKHOUSE_USER)
        self.with_env("CLICKHOUSE_PASSWORD", self.CLICKHOUSE_PASSWORD)
        self.with_env("CLICKHOUSE_DB", self.CLICKHOUSE_DB)

    def get_connection_url(self, host=None):
        return self._create_connection_url(
            dialect="clickhouse",
            username=self.CLICKHOUSE_USER,
            password=self.CLICKHOUSE_PASSWORD,
            db_name=self.CLICKHOUSE_DB,
            host=host,
            port=self.port_to_expose,
        )
