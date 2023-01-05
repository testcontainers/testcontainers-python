import sqlalchemy
from testcontainers.postgres import PostgresContainer


def test_docker_run_postgres():
    postgres_container = PostgresContainer("postgres:9.5")
    with postgres_container as postgres:
        e = sqlalchemy.create_engine(postgres.get_connection_url())
        result = e.execute("select version()")
        for row in result:
            assert row[0].lower().startswith("postgresql 9.5")


def test_docker_run_postgres_with_driver_pg8000():
    postgres_container = PostgresContainer("postgres:9.5", driver="pg8000")
    with postgres_container as postgres:
        e = sqlalchemy.create_engine(postgres.get_connection_url())
        e.execute("select 1=1")
