import os
import typing as t
from urllib.parse import quote

from testcontainers.core.container import DockerContainer
from testcontainers.core.exceptions import ContainerStartException
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.wait_strategies import HttpWaitStrategy


def asbool(obj) -> bool:
    # from sqlalchemy.util.langhelpers
    if isinstance(obj, str):
        obj = obj.strip().lower()
        if obj in ["true", "yes", "on", "y", "t", "1"]:
            return True
        elif obj in ["false", "no", "off", "n", "f", "0"]:
            return False
        else:
            raise ValueError(f"String is not true/false: {obj!r}")
    return bool(obj)


# DockerSkippingContainer, KeepaliveContainer,
class CrateDBContainer(DockerContainer):
    """
    CrateDB database container.

    Example:

        The example spins up a CrateDB database and connects to it using
        SQLAlchemy and its Python driver.

        .. doctest::

            >>> from cratedb_toolkit.testing.testcontainers.cratedb import CrateDBContainer
            >>> import sqlalchemy

            >>> cratedb_container = CrateDBContainer("crate:5.2.3")
            >>> cratedb_container.start()
            >>> with cratedb_container as cratedb:
            ...     engine = sqlalchemy.create_engine(cratedb.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("select version()"))
            ...         version, = result.fetchone()
            >>> version
            'CrateDB 5.2.3...'
    """

    CRATEDB_USER = os.environ.get("CRATEDB_USER", "crate")
    CRATEDB_PASSWORD = os.environ.get("CRATEDB_PASSWORD", "crate")
    CRATEDB_DB = os.environ.get("CRATEDB_DB", "doc")
    KEEPALIVE = asbool(os.environ.get("CRATEDB_KEEPALIVE", os.environ.get("TC_KEEPALIVE", False)))
    CMD_OPTS: t.ClassVar[dict[str, str]] = {
        "discovery.type": "single-node",
        "node.attr.storage": "hot",
        "path.repo": "/tmp/snapshots",
    }

    def __init__(
        self,
        image: str = "crate/crate:nightly",
        ports: t.Optional[dict] = None,
        user: t.Optional[str] = None,
        password: t.Optional[str] = None,
        dbname: t.Optional[str] = None,
        cmd_opts: t.Optional[dict] = None,
        **kwargs,
    ) -> None:
        """
        :param image: docker hub image path with optional tag
        :param ports: optional dict that maps a port inside the container to a port on the host machine;
                      `None` as a map value generates a random port;
                      Dicts are ordered. By convention, the first key-val pair is designated to the HTTP interface.
                      Example: {4200: None, 5432: 15432} - port 4200 inside the container will be mapped
                      to a random port on the host, internal port 5432 for PSQL interface will be mapped
                      to the 15432 port on the host.
        :param user:  optional username to access the DB; if None, try `CRATEDB_USER` environment variable
        :param password: optional password to access the DB; if None, try `CRATEDB_PASSWORD` environment variable
        :param dbname: optional database name to access the DB; if None, try `CRATEDB_DB` environment variable
        :param cmd_opts: an optional dict with CLI arguments to be passed to the DB entrypoint inside the container
        :param kwargs: misc keyword arguments
        """
        super().__init__(image=image, **kwargs)

        self._name = "testcontainers-cratedb"

        cmd_opts = cmd_opts or {}
        self._command = self._build_cmd({**self.CMD_OPTS, **cmd_opts})

        self.CRATEDB_USER = user or self.CRATEDB_USER
        self.CRATEDB_PASSWORD = password or self.CRATEDB_PASSWORD
        self.CRATEDB_DB = dbname or self.CRATEDB_DB

        self.port_mapping = ports if ports else {4200: None}
        self.port_to_expose, _ = next(iter(self.port_mapping.items()))

        self.waiting_for(HttpWaitStrategy(4200).for_status_code(200).with_startup_timeout(5))

    @staticmethod
    def _build_cmd(opts: dict) -> str:
        """
        Return a string with command options concatenated and optimised for ES5 use
        """
        cmd = []
        for key, val in opts.items():
            if isinstance(val, bool):
                val = str(val).lower()
            cmd.append(f"-C{key}={val}")
        return " ".join(cmd)

    def _configure_ports(self) -> None:
        """
        Bind all the ports exposed inside the container to the same port on the host
        """
        # If host_port is `None`, a random port to be generated
        for container_port, host_port in self.port_mapping.items():
            self.with_bind_ports(container=container_port, host=host_port)

    def _configure_credentials(self) -> None:
        self.with_env("CRATEDB_USER", self.CRATEDB_USER)
        self.with_env("CRATEDB_PASSWORD", self.CRATEDB_PASSWORD)
        self.with_env("CRATEDB_DB", self.CRATEDB_DB)

    def _configure(self) -> None:
        self._configure_ports()
        self._configure_credentials()

    def get_connection_url(self, dialect: str = "crate", host: t.Optional[str] = None) -> str:
        """
        Return a connection URL to the DB

        :param host: optional string
        :param dialect: a string with the dialect name to generate a DB URI
        :return: string containing a connection URL to te DB
        """
        # TODO: When using `db_name=self.CRATEDB_DB`:
        #       Connection.__init__() got an unexpected keyword argument 'database'
        return self._create_connection_url(
            dialect=dialect,
            username=self.CRATEDB_USER,
            password=self.CRATEDB_PASSWORD,
            host=host,
            port=self.port_to_expose,
        )

    def _create_connection_url(
        self,
        dialect: str,
        username: str,
        password: str,
        host: t.Optional[str] = None,
        port: t.Optional[int] = None,
        dbname: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> str:
        if raise_for_deprecated_parameter(kwargs, "db_name", "dbname"):
            raise ValueError(f"Unexpected arguments: {','.join(kwargs)}")
        if self._container is None:
            raise ContainerStartException("container has not been started")
        host = host or self.get_container_host_ip()
        assert port is not None
        port = self.get_exposed_port(port)
        quoted_password = quote(password, safe=" +")
        url = f"{dialect}://{username}:{quoted_password}@{host}:{port}"
        if dbname:
            url = f"{url}/{dbname}"
        return url
