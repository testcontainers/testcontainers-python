from os import environ

from testcontainers.core.generic import DbContainer


class SqlServerContainer(DbContainer):
    """
    Microsoft Sql Server database container.

    Example
    -------
    ::

        with SqlServerContainer() as mssql:
            e = sqlalchemy.create_engine(mssql.get_connection_url())
            result = e.execute("select @@VERSION")

    Notes
    -----
    Requires `ODBC Driver 17 for SQL Server <https://docs.microsoft.com/en-us/sql/connect/odbc/
    linux-mac/installing-the-microsoft-odbc-driver-for-sql-server>`_.
    """
    SQLSERVER_PASSWORD = environ.get("SQLSERVER_PASSWORD", "1Secure*Password1")

    def __init__(self, image="mcr.microsoft.com/mssql/server:2019-latest", user="SA", password=None,
                 port=1433, dbname="tempdb", driver="ODBC Driver 17 for SQL Server"):
        super(SqlServerContainer, self).__init__(image)

        self.SQLSERVER_PASSWORD = password or self.SQLSERVER_PASSWORD
        self.port_to_expose = port
        self.SQLSERVER_USER = user
        self.SQLSERVER_DBNAME = dbname
        self.SQLSERVER_DRIVER = driver

        self.with_exposed_ports(self.port_to_expose)
        self.ACCEPT_EULA = 'Y'
        self.MSSQL_PID = 'Developer'

    def _configure(self):
        self.with_env("SA_PASSWORD", self.SQLSERVER_PASSWORD)
        self.with_env("SQLSERVER_USER", self.SQLSERVER_USER)
        self.with_env("SQLSERVER_DBNAME", self.SQLSERVER_DBNAME)
        self.with_env("ACCEPT_EULA", self.ACCEPT_EULA)
        self.with_env("MSSQL_PID", self.MSSQL_PID)
        self.with_env("SQLSERVER_DRIVER", self.SQLSERVER_DRIVER)

    def get_connection_url(self):
        standard_url = super()._create_connection_url(dialect="mssql+pyodbc",
                                                      username=self.SQLSERVER_USER,
                                                      password=self.SQLSERVER_PASSWORD,
                                                      db_name=self.SQLSERVER_DBNAME,
                                                      port=self.port_to_expose)

        return standard_url + "?driver=" + self.SQLSERVER_DRIVER
