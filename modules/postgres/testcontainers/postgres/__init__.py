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
from time import sleep
from typing import Optional

from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs

_UNSET = object()


class PostgresContainer(DbContainer):
    """
    Postgres database container.

    To get a URL without a driver, pass in :code:`driver=None`.

    Example:

        The example spins up a Postgres database and connects to it using the :code:`psycopg`
        driver.

        .. doctest::

            >>> from testcontainers.postgres import PostgresContainer
            >>> import sqlalchemy

            >>> with PostgresContainer("postgres:16") as postgres:
            ...     engine = sqlalchemy.create_engine(postgres.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("select version()"))
            ...         version, = result.fetchone()
            >>> version
            'PostgreSQL 16...'
    """

    def __init__(
        self,
        image: str = "postgres:latest",
        port: int = 5432,
        username: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        driver: Optional[str] = "psycopg2",
        **kwargs,
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "user", "username")
        super().__init__(image=image, **kwargs)
        self.username: str = username or os.environ.get("POSTGRES_USER", "test")
        self.password: str = password or os.environ.get("POSTGRES_PASSWORD", "test")
        self.dbname: str = dbname or os.environ.get("POSTGRES_DB", "test")
        self.port = port
        self.driver = f"+{driver}" if driver else ""

        self.with_exposed_ports(self.port)

    def _configure(self) -> None:
        self.with_env("POSTGRES_USER", self.username)
        self.with_env("POSTGRES_PASSWORD", self.password)
        self.with_env("POSTGRES_DB", self.dbname)

    def get_connection_url(self, host: Optional[str] = None, driver: Optional[str] = _UNSET) -> str:
        """Get a DB connection URL to connect to the PG DB.

        If a driver is set in the constructor (defaults to psycopg2!), the URL will contain the
        driver. The optional driver argument to :code:`get_connection_url` overwrites the constructor
        set value. Pass :code:`driver=None` to get URLs without a driver.
        """
        driver_str = "" if driver is None else self.driver if driver is _UNSET else f"+{driver}"
        return super()._create_connection_url(
            dialect=f"postgresql{driver_str}",
            username=self.username,
            password=self.password,
            dbname=self.dbname,
            host=host,
            port=self.port,
        )

    @wait_container_is_ready()
    def _connect(self) -> None:
        wait_for_logs(self, ".*database system is ready to accept connections.*", c.max_tries, c.sleep_time)

        count = 0
        while count < c.max_tries:
            status, _ = self.exec(f"pg_isready -hlocalhost -p{self.port} -U{self.username}")
            if status == 0:
                return

            sleep(c.sleep_time)
            count += 1

        raise RuntimeError("Postgres could not get into a ready state")
