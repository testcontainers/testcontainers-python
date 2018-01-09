import pytest
import sqlalchemy

from testcontainers import MySqlContainer


@pytest.fixture(scope="session")
def mysql():
    mysql = MySqlContainer('mysql:5.7.17').start()
    engine = sqlalchemy.create_engine(mysql.get_connection_url())
    yield engine
    mysql.stop()


def test_with_mysql(mysql):
    result = mysql.execute("select version()")
    for row in result:
        assert row[0] == '5.7.17'
