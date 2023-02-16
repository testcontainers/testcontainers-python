from os import environ
from typing import Optional, Literal
from testcontainers.core.generic import DbContainer


class SqlServerContainer(DbContainer):
    """
    Microsoft SQL Server database container.

    Example:

        .. doctest::

            >>> import sqlalchemy
            >>> from testcontainers.mssql import SqlServerContainer

            >>> with SqlServerContainer() as mssql:
            ...    e = sqlalchemy.create_engine(mssql.get_connection_url())
            ...    result = e.execute("select @@VERSION")
    """

    def __init__(
        self,
        image: str = "mcr.microsoft.com/mssql/server:2019-latest",
        user: str = "SA",
        password: Optional[str] = None,
        port: int = 1433,
        dbname: str = "tempdb",
        dialect: Literal["mssql+pymssql", "mssql+pyodbc"] = "mssql+pymssql",
        **kwargs,
    ) -> None:
        """
        Initialize SqlServerContainer

        Args:
            image: MSSQL Server image. For example, use a specific version
            user: DB user name
            password: DB password
            port: Port to be exposed
            dbname: Database name
            dialect: SQLAlchemy database dialect. Allowed values are
                * 'mssql+pymssql': Uses `pymssql <https://github.com/pymssql/pymssql>`_ driver
                * 'mssql+pyodbc': Uses `pyodbc <https://github.com/mkleehammer/pyodbc>`_ driver
                This also defines the driver that is used to connect to the database.
            kwargs: Keyword arguments passed to initialization of underlying docker container
        """
        super(SqlServerContainer, self).__init__(image, **kwargs)

        self.port_to_expose = port
        self.with_exposed_ports(self.port_to_expose)

        self.SQLSERVER_PASSWORD = password or environ.get("SQLSERVER_PASSWORD", "1Secure*Password1")
        self.SQLSERVER_USER = user
        self.SQLSERVER_DBNAME = dbname
        self.dialect = dialect

    def _configure(self) -> None:
        self.with_env("SA_PASSWORD", self.SQLSERVER_PASSWORD)
        self.with_env("SQLSERVER_USER", self.SQLSERVER_USER)
        self.with_env("SQLSERVER_DBNAME", self.SQLSERVER_DBNAME)
        self.with_env("ACCEPT_EULA", "Y")

    def get_connection_url(self) -> str:
        url = super()._create_connection_url(
            dialect=self.dialect,
            username=self.SQLSERVER_USER,
            password=self.SQLSERVER_PASSWORD,
            db_name=self.SQLSERVER_DBNAME,
            port=self.port_to_expose,
        )
        if self.dialect == "mssql+pyodbc":
            url += f"?driver={self._get_url_suffix_for_latest_pyodbc_version()}"
        return url

    def _get_url_suffix_for_latest_pyodbc_version(self):
        import pyodbc
        import re

        r = re.compile(r"ODBC Driver \d{1,2} for SQL Server")
        # We sort drivers in reversed order to get the latest
        drivers = sorted(list(filter(r.match, pyodbc.drivers())), reverse=True)
        version_numbers = [int(v) for v in re.findall(r"\d{1,2}", "".join(drivers))]
        max_version_index = version_numbers.index(max(version_numbers))
        if len(drivers) > 0:
            driver_str = drivers[max_version_index].replace(" ", "+")
        else:
            raise ImportError(f"No driver available for using dialect {self.dialect}")

        return driver_str
