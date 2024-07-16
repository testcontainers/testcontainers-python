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


# This is a feature in the generic DbContainer class
# but it can't be tested on its own
# so is tested in various database modules:
# - mysql / mariadb
# - postgresql
# - sqlserver
# - mongodb
def test_quoted_password():
    user = "SA"
    # spaces seem to cause issues?
    password = "p@$%25+0&%rd:/!=?"
    quoted_password = "p%40%24%2525+0%26%25rd%3A%2F%21%3D%3F"
    driver = "pymssql"
    port = 1433
    expected_url = f"mssql+{driver}://{user}:{quoted_password}@localhost:{port}/tempdb"
    kwargs = {
        "username": user,
        "password": password,
    }
    with (
        SqlServerContainer("mcr.microsoft.com/azure-sql-edge:1.0.7", **kwargs)
        .with_env("ACCEPT_EULA", "Y")
        .with_env(
            "MSSQL_SA_PASSWORD", "{" + password + "}"
        )  # special characters have to be quoted in braces in env vars
    ) as container:
        exposed_port = container.get_exposed_port(container.port)
        expected_url = expected_url.replace(f":{port}", f":{exposed_port}")
        url = container.get_connection_url()
        assert url == expected_url
