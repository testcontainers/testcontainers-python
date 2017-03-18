import sqlalchemy as sqlalchemy

from testcontainers.mysql import MySqlContainer


def test_docker_run_mysql():
    config = MySqlContainer(version='5.7.17')
    with config as mysql:
        e = sqlalchemy.create_engine(mysql.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0] == '5.7.15'