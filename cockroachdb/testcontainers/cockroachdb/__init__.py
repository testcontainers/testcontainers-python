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
import os

from testcontainers.core.generic import DbContainer


class CockroachDbContainer(DbContainer):
    """
    Cockroach database container.

    Example
    -------
    The example spins up a Cockroach database and connects to it using the :code:`psycopg` driver.
    .. doctest::

        >>> from testcontainers.cockroachdb import CockroachDBContainer
        >>> import sqlalchemy

        >>> crdb_container = CockroachDBContainer("cockroachdb/cockroach:latest")
        >>> with crdb_container as crdb:
        ...     e = sqlalchemy.create_engine(crdb.get_connection_url())
        ...     result = e.execute("select version()")
        ...     version, = result.fetchone()
        >>> version
        'CockroachDB CCL v22.2.0...'
    """

    COCKROACH_USER = os.environ.get("COCKROACH_USER", "cockroach")
    COCKROACH_PASSWORD = os.environ.get("COCKROACH_PASSWORD", "arthropod")
    COCKROACH_DATABASE = os.environ.get("COCKROACH_DATABASE", "roach")
    REST_API_PORT = 8080
    DB_PORT = 26257

    def __init__(
        self,
        image="cockroachdb/cockroach:latest",
        user=None,
        password=None,
        dbname=None,
        driver="cockroachdb+psycopg2",
        **kwargs
    ):  # pylint: disable=too-many-arguments
        super().__init__(image=image, **kwargs)
        self.COCKROACH_USER = user or self.COCKROACH_USER
        self.COCKROACH_PASSWORD = password or self.COCKROACH_PASSWORD
        self.COCKROACH_DATABASE = dbname or self.COCKROACH_DATABASE
        self.port_to_expose = self.DB_PORT
        self.driver = driver

        cmd = "start-single-node"
        if not self.COCKROACH_PASSWORD:
            cmd += " --insecure"

        self.with_command(cmd)
        self.with_exposed_ports(self.REST_API_PORT, self.DB_PORT)

    def _configure(self):
        self.with_env("COCKROACH_USER", self.COCKROACH_USER)
        if self.COCKROACH_PASSWORD:
            self.with_env("COCKROACH_PASSWORD", self.COCKROACH_PASSWORD)
        self.with_env("COCKROACH_DATABASE", self.COCKROACH_DATABASE)

    def get_connection_url(self):
        conn_str = super()._create_connection_url(
            dialect=self.driver,
            username=self.COCKROACH_USER,
            password=self.COCKROACH_PASSWORD,
            db_name=self.COCKROACH_DATABASE,
            port=self.DB_PORT,
        )

        if self.COCKROACH_PASSWORD:
            conn_str += "?sslmode=require"

        return conn_str