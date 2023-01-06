import sqlalchemy
import pytest
from testcontainers.core.utils import is_arm
from testcontainers.mysql import MySqlContainer


@pytest.mark.skipif(is_arm(), reason='mysql container not available for ARM')
def test_docker_run_mysql():
    config = MySqlContainer('mysql:5.7.17')
    with config as mysql:
        e = sqlalchemy.create_engine(mysql.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0].startswith('5.7.17')


def test_docker_run_mariadb():
    with MySqlContainer("mariadb:10.6.5").maybe_emulate_amd64() as mariadb:
        e = sqlalchemy.create_engine(mariadb.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0].startswith('10.6.5')
