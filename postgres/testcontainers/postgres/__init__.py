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

from testcontainers.core.config import MAX_TRIES, SLEEP_TIME
from testcontainers.core.generic import DependencyFreeDbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import (wait_container_is_ready,
                                               wait_for_logs)


class PostgresContainer(DependencyFreeDbContainer):
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
    def __init__(self, image: str = "postgres:latest", port: int = 5432,
                 username: Optional[str] = None, password: Optional[str] = None,
                 dbname: Optional[str] = None, driver: str | None = "psycopg2", **kwargs) -> None:
        raise_for_deprecated_parameter(kwargs, "user", "username")
        super(PostgresContainer, self).__init__(image=image, **kwargs)
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

    def get_connection_url(self, host=None) -> str:
        return super()._create_connection_url(
            dialect=f"postgresql{self.driver}", username=self.username,
            password=self.password, dbname=self.dbname, host=host,
            port=self.port,
        )

    @wait_container_is_ready()
    def _verify_status(self) -> None:
        wait_for_logs(self, ".*database system is ready to accept connections.*", MAX_TRIES, SLEEP_TIME)

        count = 0
        while count < MAX_TRIES:
            status, _ = self.exec(f"pg_isready -hlocalhost -p{self.port} -U{self.username}")
            if status == 0:
                return

            sleep(SLEEP_TIME)
            count += 1

        raise RuntimeError("Postgres could not get into a ready state")
