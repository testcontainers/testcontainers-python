import pytest
import sqlalchemy

from testcontainers.core.utils import is_arm
from testcontainers.mssql import SqlServerContainer


@pytest.mark.skipif(is_arm(), reason="mssql container not available for ARM")
@pytest.mark.parametrize("version", ["2022-CU12-ubuntu-22.04", "2019-CU25-ubuntu-20.04"])
def test_docker_run_mssql(version: str):
    with SqlServerContainer(f"mcr.microsoft.com/mssql/server:{version}", password="1Secure*Password2") as mssql:
        engine = sqlalchemy.create_engine(mssql.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select @@servicename"))
            for row in result:
                assert row[0] == "MSSQLSERVER"


def test_docker_run_azure_sql_edge():
    with SqlServerContainer("mcr.microsoft.com/azure-sql-edge:1.0.7") as mssql:
        engine = sqlalchemy.create_engine(mssql.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select @@servicename"))
            for row in result:
                assert row[0] == "MSSQLSERVER"
