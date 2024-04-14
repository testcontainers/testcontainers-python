from os import environ
from typing import Optional

from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready


class SqlServerContainer(DbContainer):
    """
    Microsoft SQL Server database container.

    Example:

        .. doctest::

            >>> import sqlalchemy
            >>> from testcontainers.mssql import SqlServerContainer

            >>> with SqlServerContainer("mcr.microsoft.com/mssql/server:2022-CU12-ubuntu-22.04") as mssql:
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
        **kwargs,
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "user", "username")
        super().__init__(image, **kwargs)

        self.port = port
        self.with_exposed_ports(self.port)

        self.password = password or environ.get("SQLSERVER_PASSWORD", "1Secure*Password1")
        self.username = username
        self.dbname = dbname
        self.dialect = dialect

    def _configure(self) -> None:
        self.with_env("SA_PASSWORD", self.password)
        self.with_env("SQLSERVER_USER", self.username)
        self.with_env("SQLSERVER_DBNAME", self.dbname)
        self.with_env("ACCEPT_EULA", "Y")

    @wait_container_is_ready(AssertionError)
    def _connect(self) -> None:
        status, _ = self.exec(f"/opt/mssql-tools/bin/sqlcmd -U {self.username} -P {self.password} -Q 'SELECT 1'")
        assert status == 0, "Cannot run 'SELECT 1': container is not ready"

    def get_connection_url(self) -> str:
        return super()._create_connection_url(
            dialect=self.dialect, username=self.username, password=self.password, dbname=self.dbname, port=self.port
        )
