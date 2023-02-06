import re

import sqlalchemy
from testcontainers.mssql import SqlServerContainer
from unittest.mock import patch


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


def test_get_url_suffix_for_latest_pyodbc_version():
    container = SqlServerContainer()

    version_numbers = [10, 8]
    with patch("pyodbc.drivers", return_value=[f'ODBC Driver {v} for SQL Server' for v in version_numbers]):
         driver_str = container._get_url_suffix_for_latest_pyodbc_version()
         latest_version = int(re.findall('\d{1,2}', driver_str)[0])
    assert latest_version == max(version_numbers)
