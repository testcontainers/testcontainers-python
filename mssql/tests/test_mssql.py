import sqlalchemy
from testcontainers.mssql import SqlServerContainer


def test_docker_run_mssql():
    image = 'mcr.microsoft.com/azure-sql-edge'
    dialects = ['mssql+pymssql', 'mssql+pyodbc']
    for dialect in dialects:
        with SqlServerContainer(dialect=dialect) as mssql:
            e = sqlalchemy.create_engine(mssql.get_connection_url())
            result = e.execute('select @@servicename')
            for row in result:
                assert row[0] == 'MSSQLSERVER'

    with SqlServerContainer(image, password="1Secure*Password2", dialect=dialect) as mssql:
        e = sqlalchemy.create_engine(mssql.get_connection_url())
        result = e.execute('select @@servicename')
        for row in result:
            assert row[0] == 'MSSQLSERVER'
