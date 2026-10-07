import sqlalchemy
from trino.dbapi import connect

from testcontainers.community.trino import TrinoContainer


def test_docker_run_trino():
    container = TrinoContainer("trinodb/trino:451")
    with container as trino:
        conn = connect(
            host=trino.get_container_host_ip(),
            port=trino.get_exposed_port(trino.port),
            user="test",
        )
        cur = conn.cursor()
        cur.execute("SELECT version()")
        rows = cur.fetchall()
        assert rows[0][0] == "451"
        conn.close()


def test_get_connection_url():
    container = TrinoContainer("trinodb/trino:451")
    with container as trino:
        engine = sqlalchemy.create_engine(trino.get_connection_url())
        with engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("SELECT version()"))
            assert result.fetchone()[0] == "451"
