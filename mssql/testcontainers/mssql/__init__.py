from os import environ
from typing import Optional
from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter


class SqlServerContainer(DbContainer):
    """
    Microsoft SQL Server database container.

    Example:

        .. doctest::

            >>> import sqlalchemy
            >>> from testcontainers.mssql import SqlServerContainer

        >>> with SqlServerContainer() as mssql:
        ...    engine = sqlalchemy.create_engine(mssql.get_connection_url())
        ...    result = engine.execute(sqlalchemy.text("select @@VERSION"))
    Notes
    -----
    Requires `ODBC Driver 17 for SQL Server <https://docs.microsoft.com/en-us/sql/connect/odbc/
    linux-mac/installing-the-microsoft-odbc-driver-for-sql-server>`_.
    """

    def __init__(self, image: str = "mcr.microsoft.com/mssql/server:2019-latest",
                 username: str = "SA", password: Optional[str] = None, port: int = 1433,
                 dbname: str = "tempdb", dialect: str = 'mssql+pymssql', driver: str = "ODBC Driver 17 for SQL Server", **kwargs) -> None:
        raise_for_deprecated_parameter(kwargs, "user", "username")
        super(SqlServerContainer, self).__init__(image, **kwargs)

        self.port = port
        self.with_exposed_ports(self.port)

        self.password = password or environ.get("SQLSERVER_PASSWORD", "1Secure*Password1")
        self.username = username
        self.dbname = dbname
        self.dialect = dialect
        self.driver = driver

    def _configure(self) -> None:
        self.with_env("SA_PASSWORD", self.password)
        self.with_env("SQLSERVER_USER", self.username)
        self.with_env("SQLSERVER_DBNAME", self.dbname)
        self.with_env("ACCEPT_EULA", 'Y')

    def get_connection_url(self) -> str:
        base_url = super(SqlServerContainer, self)._create_connection_url(
            dialect=self.dialect, username=self.username, password=self.password,
            db_name=self.dbname, port=self.port
        )
        url = base_url + f"?driver={'+'.join(self.driver.split(' '))}"
        return url

