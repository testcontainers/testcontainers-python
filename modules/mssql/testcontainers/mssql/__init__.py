from os import environ
from typing import Optional

from typing_extensions import override

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import create_connection_string, raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready

ADDITIONAL_TRANSIENT_ERRORS = []
try:
    from sqlalchemy.exc import DBAPIError

    ADDITIONAL_TRANSIENT_ERRORS.append(DBAPIError)
except ImportError:
    pass


class SqlServerContainer(DockerContainer):
    """
    Microsoft SQL Server database container.

    Example:

        .. doctest::

            >>> import sqlalchemy
            >>> from testcontainers.mssql import SqlServerContainer

            >>> with SqlServerContainer("mcr.microsoft.com/azure-sql-edge:1.0.7") as mssql:
            ...    engine = sqlalchemy.create_engine(mssql.get_connection_url())
            ...    with engine.begin() as connection:
            ...        result = connection.execute(sqlalchemy.text("select @@VERSION"))
    """

    def __init__(
        self,
        image: str = "mcr.microsoft.com/mssql/server:2019-latest",
        username: str = "SA",
        password: Optional[str] = None,
        port: int = 1433,
        dbname: str = "tempdb",
        dialect: str = "mssql+pymssql",
        **kwargs
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "user", "username")
        super().__init__(image, **kwargs)

        self.port = port
        self.with_exposed_ports(self.port)

        self.password = password or environ.get("SQLSERVER_PASSWORD", "1Secure*Password1")
        self.username = username
        self.dbname = dbname
        self.dialect = dialect

    @wait_container_is_ready(*ADDITIONAL_TRANSIENT_ERRORS)
    def _wait_until_ready(self):
        import sqlalchemy

        engine = sqlalchemy.create_engine(self.get_connection_url())
        try:
            engine.connect()
        finally:
            engine.dispose()

    @override
    def _configure(self) -> None:
        self.with_env("SA_PASSWORD", self.password)
        self.with_env("SQLSERVER_USER", self.username)
        self.with_env("SQLSERVER_DBNAME", self.dbname)
        self.with_env("ACCEPT_EULA", "Y")

    def get_connection_url(self) -> str:
        return create_connection_string(
            dialect=self.dialect,
            username=self.username,
            password=self.password,
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.port),
            dbname=self.dbname,
        )
