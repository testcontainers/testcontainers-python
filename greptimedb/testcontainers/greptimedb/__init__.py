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

from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter


class GreptimeDBContainer(DbContainer):
    """
    GreptimeDB database container.

    Example:

        The example will spin up a GreptimeDB database to which you can connect with the credentials
        passed in the constructor. Alternatively, you may use the :code:`get_connection_url()`
        method which returns a sqlalchemy-compatible url in format
        :code:`dialect+driver://username:password@host:port/database`.

        .. doctest::

            >>> import sqlalchemy
            >>> from testcontainers.greptimedb import GreptimeDBContainer

            >>> with GreptimeDBContainer('greptime/greptimedb:v0.4.3') as greptimedb:
            ...     engine = sqlalchemy.create_engine(greptimedb.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("select version()"))
            ...         version, = result.fetchone()
    """

    def __init__(
        self,
        image: str = "greptimedb:latest",
        username: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        http_port: int = 4000,
        grpc_port: int = 4001,
        mysql_port: int = 4002,
        pg_port: int = 4003,
        **kwargs,
    ) -> None:
        super(GreptimeDBContainer, self).__init__(image, **kwargs)

        self.http_port = http_port
        self.grpc_port = grpc_port
        self.mysql_port = mysql_port
        self.pg_port = pg_port

        self.username = username or environ.get("GREPTIMEDB_USER", "test")
        self.password = password or environ.get("GREPTIMEDB_PASSWORD", "test")
        self.dbname = dbname or environ.get("GREPTIMEDB_DATABASE", "public")

        self.with_exposed_ports(
            self.http_port,
            self.grpc_port,
            self.mysql_port,
            self.pg_port,
        )

    def _configure(self) -> None:
        self.with_env("GREPTIMEDB_USER", self.username)
        self.with_env("GREPTIMEDB_PASSWORD", self.password)
        self.with_env("GREPTIMEDB_DATABASE", self.dbname)

    def get_connection_url(self) -> str:
        return super()._create_connection_url(
            dialect="mysql+pymysql",
            username=self.username,
            password=self.password,
            dbname=self.dbname,
            port=self.mysql_port,
        )
