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

from testcontainers.core.generic import DbContainer


class PostgresContainer(DbContainer):
    """
    Postgres database container.

    Example
    -------
    The example spins up a Postgres database and connects to it using the :code:`psycopg` driver.
    .. doctest::

        >>> from testcontainers.postgres import PostgresContainer
        >>> import sqlalchemy

        >>> postgres_container = PostgresContainer("postgres:9.5")
        >>> with postgres_container as postgres:
        ...     e = sqlalchemy.create_engine(postgres.get_connection_url())
        ...     result = e.execute("select version()")
        ...     version, = result.fetchone()
        >>> version
        'PostgreSQL 9.5...'
    """
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "test")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "test")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "test")
    POSTGRES_INITDB_ARGS = os.environ.get("POSTGRES_INITDB_ARGS", None)
    POSTGRES_INITDB_WALDIR = os.environ.get("POSTGRES_INITDB_WALDIR", None)
    POSTGRES_HOST_AUTH_METHOD = os.environ.get("POSTGRES_HOST_AUTH_METHOD", None)
    PGDATA = os.environ.get("PGDATA", None)

    env_names = [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_INITDB_ARGS",
        "POSTGRES_INITDB_WALDIR",
        "POSTGRES_HOST_AUTH_METHOD",
        "PGDATA"
    ]

    def __init__(self,
                 image="postgres:latest",
                 port=5432, user=None,
                 password=None,
                 dbname=None,
                 driver="psycopg2",
                 initdb_args=None,
                 initdb_waldir=None,
                 host_auth_method=None,
                 pgdata=None,
                 **kwargs):
        super(PostgresContainer, self).__init__(image=image, **kwargs)
        self.POSTGRES_USER = user or self.POSTGRES_USER
        self.POSTGRES_PASSWORD = password or self.POSTGRES_PASSWORD
        self.POSTGRES_DB = dbname or self.POSTGRES_DB
        self.port_to_expose = port
        self.driver = driver
        self.POSTGRES_INITDB_ARGS = initdb_args or self.POSTGRES_INITDB_ARGS
        self.POSTGRES_INITDB_WALDIR = initdb_waldir or self.POSTGRES_INITDB_WALDIR
        self.POSTGRES_HOST_AUTH_METHOD = host_auth_method or self.POSTGRES_HOST_AUTH_METHOD
        self.PGDATA = pgdata or self.PGDATA
        self.with_exposed_ports(self.port_to_expose)

    def _configure(self):
        for env_name in self.env_names:
            if getattr(self, env_name) is not None:
                self.with_env(env_name, getattr(self, env_name))

    def get_connection_url(self, host=None):
        return super()._create_connection_url(dialect="postgresql+{}".format(self.driver),
                                              username=self.POSTGRES_USER,
                                              password=self.POSTGRES_PASSWORD,
                                              db_name=self.POSTGRES_DB,
                                              host=host,
                                              port=self.port_to_expose)
