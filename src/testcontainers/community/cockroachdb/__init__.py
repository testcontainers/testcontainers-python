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
from os import environ
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class CockroachDBContainer(DbContainer):
    """
    CockroachDB database container.

    Example:

        The example will spin up a CockroachDB database to which you can connect with the credentials
        passed in the constructor. Alternatively, you may use the :code:`get_connection_url()`
        method which returns a sqlalchemy-compatible url in format
        :code:`dialect+driver://username:password@host:port/database`.

        .. doctest::

            >>> import sqlalchemy
            >>> from testcontainers.cockroachdb import CockroachDBContainer

            >>> with CockroachDBContainer('cockroachdb/cockroach:v24.1.1') as crdb:
            ...     engine = sqlalchemy.create_engine(crdb.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("select version()"))
            ...         version, = result.fetchone()

    """

    COCKROACH_DB_PORT: int = 26257
    COCKROACH_API_PORT: int = 8080

    def __init__(
        self,
        image: str = "cockroachdb/cockroach:v24.1.1",
        username: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        dialect="cockroachdb+psycopg2",
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)

        self.with_exposed_ports(self.COCKROACH_DB_PORT, self.COCKROACH_API_PORT)
        self.username = username or environ.get("COCKROACH_USER", "cockroach")
        self.password = password or environ.get("COCKROACH_PASSWORD", "arthropod")
        self.dbname = dbname or environ.get("COCKROACH_DATABASE", "roach")
        self.dialect = dialect

    def _configure(self) -> None:
        self.with_env("COCKROACH_DATABASE", self.dbname)
        self.with_env("COCKROACH_USER", self.username)
        self.with_env("COCKROACH_PASSWORD", self.password)

        cmd = "start-single-node"
        if not self.password:
            cmd += " --insecure"
        self.with_command(cmd)

    @wait_container_is_ready(HTTPError, URLError)
    def _connect(self) -> None:
        host = self.get_container_host_ip()
        url = f"http://{host}:{self.get_exposed_port(self.COCKROACH_API_PORT)}/health"
        self._wait_for_health(url)
        wait_for_logs(self, "finished creating default user*")

    @staticmethod
    def _wait_for_health(url):
        with urlopen(url) as response:
            response.read()

    def get_connection_url(self) -> str:
        conn_str = super()._create_connection_url(
            dialect=self.dialect,
            username=self.username,
            password=self.password,
            dbname=self.dbname,
            port=self.COCKROACH_DB_PORT,
        )

        if self.password:
            conn_str += "?sslmode=require"

        return conn_str
