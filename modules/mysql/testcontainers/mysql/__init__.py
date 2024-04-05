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


class MySqlContainer(DbContainer):
    """
    MySql database container.

    Example:

        The example will spin up a MySql database to which you can connect with the credentials
        passed in the constructor. Alternatively, you may use the :code:`get_connection_url()`
        method which returns a sqlalchemy-compatible url in format
        :code:`dialect+driver://username:password@host:port/database`.

        .. doctest::

            >>> import sqlalchemy
            >>> from testcontainers.mysql import MySqlContainer

            >>> with MySqlContainer('mysql:5.7.17') as mysql:
            ...     engine = sqlalchemy.create_engine(mysql.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("select version()"))
            ...         version, = result.fetchone()
    """

    def __init__(
        self,
        image: str = "mysql:latest",
        username: Optional[str] = None,
        root_password: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        port: int = 3306,
        **kwargs,
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "MYSQL_USER", "username")
        raise_for_deprecated_parameter(kwargs, "MYSQL_ROOT_PASSWORD", "root_password")
        raise_for_deprecated_parameter(kwargs, "MYSQL_PASSWORD", "password")
        raise_for_deprecated_parameter(kwargs, "MYSQL_DATABASE", "dbname")
        super().__init__(image, **kwargs)

        self.port = port
        self.with_exposed_ports(self.port)
        self.username = username or environ.get("MYSQL_USER", "test")
        self.root_password = root_password or environ.get("MYSQL_ROOT_PASSWORD", "test")
        self.password = password or environ.get("MYSQL_PASSWORD", "test")
        self.dbname = dbname or environ.get("MYSQL_DATABASE", "test")

        if self.username == "root":
            self.root_password = self.password

    def _configure(self) -> None:
        self.with_env("MYSQL_ROOT_PASSWORD", self.root_password)
        self.with_env("MYSQL_DATABASE", self.dbname)

        if self.username != "root":
            self.with_env("MYSQL_USER", self.username)
            self.with_env("MYSQL_PASSWORD", self.password)

    def get_connection_url(self) -> str:
        return super()._create_connection_url(
            dialect="mysql+pymysql", username=self.username, password=self.password, dbname=self.dbname, port=self.port
        )
