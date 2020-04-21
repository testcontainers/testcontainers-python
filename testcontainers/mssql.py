from os import environ

from testcontainers.core.generic import DbContainer


class SqlServerContainer(DbContainer):
    SQLSERVER_PASSWORD = environ.get("SQLSERVER_PASSWORD", "1Secure*Password1")
    SQLSERVER_USER = "SA"
    SQLSERVER_DBNAME = "tempdb"
    SQLSERVER_DRIVER = "ODBC Driver 17 for SQL Server"

    def __init__(self, image="mcr.microsoft.com/mssql/server:2019-latest", **kwargs):
        super(SqlServerContainer, self).__init__(image)
        self.port_to_expose = 1433
        self.with_exposed_ports(self.port_to_expose)
        self.ACCEPT_EULA = 'Y'
        self.MSSQL_PID = 'Developer'

        if 'SQLSERVER_PASSWORD' in kwargs:
            self.SQLSERVER_PASSWORD = kwargs['SQLSERVER_PASSWORD']
        if 'SQLSERVER_USER' in kwargs:
            self.SQLSERVER_USER = kwargs['SQLSERVER_USER']
        if 'SQLSERVER_DBNAME' in kwargs:
            self.SQLSERVER_DBNAME = kwargs['SQLSERVER_DBNAME']
        if 'SQLSERVER_DRIVER' in kwargs:
            self.SQLSERVER_DRIVER = kwargs['SQLSERVER_DRIVER']

    def _configure(self):
        self.with_env("SA_PASSWORD", self.SQLSERVER_PASSWORD)
        self.with_env("SQLSERVER_USER", self.SQLSERVER_USER)
        self.with_env("SQLSERVER_DBNAME", self.SQLSERVER_DBNAME)
        self.with_env("ACCEPT_EULA", self.ACCEPT_EULA)
        self.with_env("MSSQL_PID", self.MSSQL_PID)

    def get_connection_url(self):
        standard_url = super()._create_connection_url(dialect="mssql+pyodbc",
                                                      username=self.SQLSERVER_USER,
                                                      password=self.SQLSERVER_PASSWORD,
                                                      db_name=self.SQLSERVER_DBNAME,
                                                      port=self.port_to_expose)

        return standard_url + "?driver=" + self.SQLSERVER_DRIVER
