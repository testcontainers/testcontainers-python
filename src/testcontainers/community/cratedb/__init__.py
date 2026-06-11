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
from typing import ClassVar, Optional

from testcontainers.community.generic.sql import SqlContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.wait_strategies import HttpWaitStrategy

# CrateDB's HTTP interface. The SQLAlchemy `crate://` dialect talks to CrateDB
# over HTTP, so this is the port used for connection URLs and readiness checks.
HTTP_PORT = 4200
# CrateDB's PostgreSQL wire-protocol interface, exposed for convenience.
PSQL_PORT = 5432


class CrateDBContainer(SqlContainer):
    """
    CrateDB database container.

    Example:

        The example spins up a CrateDB database and connects to it using
        SQLAlchemy and the ``sqlalchemy-cratedb`` dialect, which talks to
        CrateDB over its HTTP interface (port 4200).

        .. doctest::

            >>> from testcontainers.community.cratedb import CrateDBContainer
            >>> import sqlalchemy

            >>> with CrateDBContainer("crate:5.10") as cratedb:
            ...     engine = sqlalchemy.create_engine(cratedb.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("select name from sys.cluster"))
            ...         cluster_name, = result.fetchone()
    """

    # Default command-line options. CrateDB needs single-node discovery to run
    # as a one-node cluster suitable for testing.
    CMD_OPTS: ClassVar[dict[str, str]] = {"discovery.type": "single-node"}

    def __init__(
        self,
        image: str = "crate/crate:latest",
        port: int = HTTP_PORT,
        username: Optional[str] = None,
        password: Optional[str] = None,
        dialect: str = "crate",
        cmd_opts: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> None:
        """
        :param image: Docker image name (with optional tag).
        :param port: container port used to build the connection URL; defaults
                     to the HTTP port (4200) used by the ``crate://`` dialect.
        :param username: username for the DB; falls back to the ``CRATEDB_USER``
                         environment variable, then ``crate``.
        :param password: password for the DB; falls back to the
                         ``CRATEDB_PASSWORD`` environment variable, then ``crate``.
        :param dialect: SQLAlchemy dialect used in the connection URL.
        :param cmd_opts: extra ``-C<key>=<value>`` options passed to CrateDB,
                         merged over (and able to override) the defaults.
        """
        raise_for_deprecated_parameter(kwargs, "user", "username")
        # Readiness is signalled by CrateDB's HTTP interface returning 200; this
        # keeps startup free of any database client library.
        super().__init__(image, wait_strategy=HttpWaitStrategy(HTTP_PORT).for_status_code(200), **kwargs)

        cmd_opts = cmd_opts or {}
        self._command = self._build_cmd({**self.CMD_OPTS, **cmd_opts})

        self.username = username or os.environ.get("CRATEDB_USER", "crate")
        self.password = password or os.environ.get("CRATEDB_PASSWORD", "crate")
        self.port = port
        self.dialect = dialect

        self.with_exposed_ports(HTTP_PORT, PSQL_PORT)

    @staticmethod
    def _build_cmd(opts: dict[str, str]) -> str:
        """Render a CrateDB ``-C<key>=<value> ...`` command-line string."""
        cmd = []
        for key, val in opts.items():
            if isinstance(val, bool):
                val = str(val).lower()
            cmd.append(f"-C{key}={val}")
        return " ".join(cmd)

    def _configure(self) -> None:
        self.with_env("CRATEDB_USER", self.username)
        self.with_env("CRATEDB_PASSWORD", self.password)

    def get_connection_url(self, host: Optional[str] = None) -> str:
        return self._create_connection_url(
            dialect=self.dialect,
            username=self.username,
            password=self.password,
            host=host,
            port=self.port,
        )
