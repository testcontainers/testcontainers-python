from os import environ

from testcontainers.core.generic import DbContainer


class SqlServerContainer(DbContainer):
    """
    Microsoft Sql Server database container.

    Example
    -------
    .. doctest::

        >>> import sqlalchemy
        >>> from testcontainers.mssql import SqlServerContainer

        >>> with SqlServerContainer() as mssql:
        ...    e = sqlalchemy.create_engine(mssql.get_connection_url())
        ...    result = e.execute("select @@VERSION")

    Notes
    -----
    Requires `ODBC Driver 17 for SQL Server <https://docs.microsoft.com/en-us/sql/connect/odbc/
    linux-mac/installing-the-microsoft-odbc-driver-for-sql-server>`_.
    """

    def __init__(self, image="mcr.microsoft.com/mssql/server:2019-latest", user="SA", password=None,
                 port=1433, dbname="tempdb", dialect='mssql+pymssql', **kwargs):
        super(SqlServerContainer, self).__init__(image, **kwargs)

        self.SQLSERVER_PASSWORD = password or environ.get("SQLSERVER_PASSWORD", "1Secure*Password1")
        self.port_to_expose = port
        self.SQLSERVER_USER = user
        self.SQLSERVER_DBNAME = dbname
        self.dialect = dialect

    def _configure(self):
        self.with_exposed_ports(self.port_to_expose)
        self.with_env("SA_PASSWORD", self.SQLSERVER_PASSWORD)
        self.with_env("SQLSERVER_USER", self.SQLSERVER_USER)
        self.with_env("SQLSERVER_DBNAME", self.SQLSERVER_DBNAME)
        self.with_env("ACCEPT_EULA", 'Y')

    def get_connection_url(self):
        return super()._create_connection_url(
            dialect=self.dialect, username=self.SQLSERVER_USER, password=self.SQLSERVER_PASSWORD,
            db_name=self.SQLSERVER_DBNAME, port=self.port_to_expose
        )
