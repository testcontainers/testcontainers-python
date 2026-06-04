import sqlalchemy

from testcontainers.cockroachdb import CockroachDBContainer


def test_docker_run_mysql():
    config = CockroachDBContainer("cockroachdb/cockroach:v24.1.1")
    with config as crdb:
        engine = sqlalchemy.create_engine(crdb.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert "CockroachDB" in row[0]
                assert "v24.1.1" in row[0]
