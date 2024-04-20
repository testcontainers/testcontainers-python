import re
from unittest import mock

import pytest
import sqlalchemy

from testcontainers.core.utils import is_arm
from testcontainers.mysql import MySqlContainer


def test_docker_run_mysql():
    config = MySqlContainer("mysql:8.3.0")
    with config as mysql:
        engine = sqlalchemy.create_engine(mysql.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert row[0].startswith("8.3.0")


@pytest.mark.skipif(is_arm(), reason="mysql container not available for ARM")
def test_docker_run_legacy_mysql():
    config = MySqlContainer("mysql:5.7.44")
    with config as mysql:
        engine = sqlalchemy.create_engine(mysql.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert row[0].startswith("5.7.44")


@pytest.mark.parametrize("version", ["11.3.2", "10.11.7"])
def test_docker_run_mariadb(version: str):
    with MySqlContainer(f"mariadb:{version}") as mariadb:
        engine = sqlalchemy.create_engine(mariadb.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert row[0].startswith(version)


def test_docker_env_variables():
    with (
        mock.patch.dict("os.environ", MYSQL_USER="demo", MYSQL_DATABASE="custom_db"),
        MySqlContainer("mariadb:10.6.5").with_bind_ports(3306, 32785) as container,
    ):
        url = container.get_connection_url()
        pattern = r"mysql\+pymysql:\/\/demo:test@[\w,.]+:(3306|32785)\/custom_db"
        assert re.match(pattern, url)


# This is a feature in the generic DbContainer class
# but it can't be tested on its own
# so is tested in various database modules:
# - mysql / mariadb
# - postgresql
# - sqlserver
# - mongodb
def test_quoted_password():
    user = "root"
    password = "p@$%25+0&%rd :/!=?"
    quoted_password = "p%40%24%2525+0%26%25rd %3A%2F%21%3D%3F"
    driver = "pymysql"
    with MySqlContainer("mariadb:10.6.5", username=user, password=password) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(3306)
        expected_url = f"mysql+{driver}://{user}:{quoted_password}@{host}:{port}/test"
        url = container.get_connection_url()
        assert url == expected_url

        with sqlalchemy.create_engine(expected_url).begin() as connection:
            connection.execute(sqlalchemy.text("select version()"))

        raw_pass_url = f"mysql+{driver}://{user}:{password}@{host}:{port}/test"
        with pytest.raises(Exception):
            with sqlalchemy.create_engine(raw_pass_url).begin() as connection:
                connection.execute(sqlalchemy.text("select version()"))
