import sqlalchemy
from testcontainers.mssql import SqlServerContainer


def test_docker_run_mssql():
    image = 'mcr.microsoft.com/azure-sql-edge'
    dialects = ['mssql+pymssql', 'mssql+pyodbc']
    ends_withs = ["tempdb", "for+SQL+Server"]
    for dialect, end_with in zip(dialects, ends_withs):
        with SqlServerContainer(dialect=dialect) as mssql:
            url = mssql.get_connection_url()
            assert url.endswith(end_with)
            e = sqlalchemy.create_engine(url)
            result = e.execute('select @@servicename')
            for row in result:
                assert row[0] == 'MSSQLSERVER'

    with SqlServerContainer(image, password="1Secure*Password2", dialect=dialect) as mssql:
        e = sqlalchemy.create_engine(mssql.get_connection_url())
        result = e.execute('select @@servicename')
        for row in result:
            assert row[0] == 'MSSQLSERVER'
