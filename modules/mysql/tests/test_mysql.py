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


@pytest.mark.skipif(is_arm(), reason="mysql container not available for ARM")
def test_docker_run_mysql_8_seed():
    seeds = ("modules/mysql/tests/", ["schema.sql", "seeds.sql"])
    config = MySqlContainer("mysql:8", seed=seeds)
    with config as mysql:
        engine = sqlalchemy.create_engine(mysql.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select * from stuff"))
            assert len(list(result)) == 4, "Should have gotten all the stuff"


@pytest.mark.skipif(is_arm(), reason="mysql container not available for ARM")
def test_docker_run_mysql_8_seed_missing():
    seeds = ("modules/mysql/tests/", ["schema.sql", "nosuchfile.sql"])
    config = MySqlContainer("mysql:8", seed=seeds)
    with pytest.raises(ValueError, match="Error seeding the database with script"):
        with config as mysql:
            pass


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
