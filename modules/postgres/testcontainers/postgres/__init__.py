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

from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter


class PostgresContainer(DbContainer):
    """
    Postgres database container.

    Example:

        The example spins up a Postgres database and connects to it using the :code:`psycopg`
        driver.

        .. doctest::

            >>> from testcontainers.postgres import PostgresContainer
            >>> import sqlalchemy

            >>> postgres_container = PostgresContainer("postgres:9.5")
            >>> with postgres_container as postgres:
            ...     engine = sqlalchemy.create_engine(postgres.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("select version()"))
            ...         version, = result.fetchone()
            >>> version
            'PostgreSQL 9.5...'
    """

    def __init__(
        self,
        image: str = "postgres:latest",
        port: int = 5432,
        username: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        driver: str = "psycopg2",
        **kwargs,
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "user", "username")
        super().__init__(image=image, **kwargs)
        self.username = username or os.environ.get("POSTGRES_USER", "test")
        self.password = password or os.environ.get("POSTGRES_PASSWORD", "test")
        self.dbname = dbname or os.environ.get("POSTGRES_DB", "test")
        self.port = port
        self.driver = driver

        self.with_exposed_ports(self.port)

    def _configure(self) -> None:
        self.with_env("POSTGRES_USER", self.username)
        self.with_env("POSTGRES_PASSWORD", self.password)
        self.with_env("POSTGRES_DB", self.dbname)

    def get_connection_url(self, host=None) -> str:
        return super()._create_connection_url(
            dialect=f"postgresql+{self.driver}",
            username=self.username,
            password=self.password,
            dbname=self.dbname,
            host=host,
            port=self.port,
        )
