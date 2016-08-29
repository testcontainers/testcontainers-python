import psycopg2
import sqlalchemy

from testcontainers.mysql import MySqlContainer
from testcontainers.postgres import PostgresContainer


def test_docker_run_mysql():
    config = MySqlContainer("user", "secret", version="5.7")
    with config as mysql:
        e = sqlalchemy.create_engine(mysql.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0] == '5.7.14'


def test_docker_run_postgress():
    postgres_container = PostgresContainer("user", "secret", version="9.5")
    with postgres_container as postgres:
        conn = psycopg2.connect(host=postgres.host_ip,
                                user=postgres.username,
                                password=postgres.password,
                                database=postgres.database)
        cur = conn.cursor()

        cur.execute("SELECT VERSION()")
        row = cur.fetchone()
        print("server version:", row[0])
        cur.close()
        assert len(row) > 0
