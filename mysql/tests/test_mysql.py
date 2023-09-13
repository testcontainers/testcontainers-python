import re
import sqlalchemy
import pytest
from testcontainers.core.utils import is_arm
from testcontainers.mysql import MySqlContainer
from unittest import mock


@pytest.mark.skipif(is_arm(), reason='mysql container not available for ARM')
def test_docker_run_mysql():
    config = MySqlContainer('mysql:5.7.17')
    with config as mysql:
        engine = sqlalchemy.create_engine(mysql.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert row[0].startswith('5.7.17')


@pytest.mark.skipif(is_arm(), reason='mysql container not available for ARM')
def test_docker_run_mysql_8():
    config = MySqlContainer('mysql:8')
    with config as mysql:
        engine = sqlalchemy.create_engine(mysql.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert row[0].startswith('8')


def test_docker_run_mariadb():
    with MySqlContainer("mariadb:10.6.5").maybe_emulate_amd64() as mariadb:
        engine = sqlalchemy.create_engine(mariadb.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert row[0].startswith('10.6.5')


def test_docker_env_variables():
    with mock.patch.dict("os.environ", MYSQL_USER="demo", MYSQL_DATABASE="custom_db"), \
        MySqlContainer("mariadb:10.6.5").with_bind_ports(3306, 32785).maybe_emulate_amd64() \
            as container:
        url = container.get_connection_url()
        pattern = r'mysql\+pymysql:\/\/demo:test@[\w,.]+:(3306|32785)\/custom_db'
        assert re.match(pattern, url)
