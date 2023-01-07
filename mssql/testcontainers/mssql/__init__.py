from os import environ
from typing import Optional
from testcontainers.core.generic import DbContainer


class SqlServerContainer(DbContainer):
    """
    Microsoft SQL Server database container.

    Example:

        .. doctest::

            >>> import sqlalchemy
            >>> from testcontainers.mssql import SqlServerContainer

            >>> with SqlServerContainer() as mssql:
            ...    engine = sqlalchemy.create_engine(mssql.get_connection_url())
            ...    with engine.begin() as connection:
            ...        result = connection.execute(sqlalchemy.text("select @@VERSION"))
    """

    def __init__(self, image: str = "mcr.microsoft.com/mssql/server:2019-latest",
                 username: str = "SA", password: Optional[str] = None, port: int = 1433,
                 dbname: str = "tempdb", dialect: str = 'mssql+pymssql', user: None = None,
                 **kwargs) -> None:
        super(SqlServerContainer, self).__init__(image, **kwargs)
        if user:
            raise ValueError("use `username` instead")

        self.port_to_expose = port
        self.with_exposed_ports(self.port_to_expose)

        self.password = password or environ.get("SQLSERVER_PASSWORD", "1Secure*Password1")
        self.username = username
        self.dbname = dbname
        self.dialect = dialect

    def _configure(self) -> None:
        self.with_env("SA_PASSWORD", self.password)
        self.with_env("SQLSERVER_USER", self.username)
        self.with_env("SQLSERVER_DBNAME", self.dbname)
        self.with_env("ACCEPT_EULA", 'Y')

    def get_connection_url(self) -> str:
        return super()._create_connection_url(
            dialect=self.dialect, username=self.username, password=self.password,
            db_name=self.dbname, port=self.port_to_expose
        )
