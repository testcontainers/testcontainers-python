from sqlalchemy import create_engine, text
from testcontainers.cockroachdb import CockroachDbContainer


def test_docker_run_cockroachdb():
    with CockroachDbContainer("cockroachdb/cockroach:latest") as crdb:
        with create_engine(crdb.get_connection_url()).connect() as conn:
            result = conn.execute(text("select version();"))
            assert "CockroachDB" in result.first().version


def test_docker_run_cockroachdb_with_user_and_pass():
    with CockroachDbContainer(
        "cockroachdb/cockroach:latest", user="geralt", password="unicorn"
    ) as crdb:
        with create_engine(crdb.get_connection_url()).connect() as conn:
            result = conn.execute(text("select version();"))
            assert "CockroachDB" in result.first().version
