import pytest

from testcontainers.postgres import PostgresContainer
import sqlalchemy


# https://www.postgresql.org/support/versioning/
@pytest.mark.parametrize("version", ["12", "13", "14", "15", "16", "latest"])
def test_docker_run_postgres(version: str, monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("SQLA was called during PG container setup")

    monkeypatch.setattr(sqlalchemy, "create_engine", fail)
    postgres_container = PostgresContainer(f"postgres:{version}")
    with postgres_container as postgres:
        status, msg = postgres.exec(f"pg_isready -hlocalhost -p{postgres.port} -U{postgres.username}")

        assert msg.decode("utf-8").endswith("accepting connections\n")
        assert status == 0

        status, msg = postgres.exec(
            f"psql -hlocalhost -p{postgres.port} -U{postgres.username} -c 'select 2*3*5*7*11*13*17 as a;' "
        )
        assert "510510" in msg.decode("utf-8")
        assert "(1 row)" in msg.decode("utf-8")
        assert status == 0


def test_docker_run_postgres_with_sqlalchemy():
    postgres_container = PostgresContainer("postgres:9.5")
    with postgres_container as postgres:
        engine = sqlalchemy.create_engine(postgres.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert row[0].lower().startswith("postgresql 9.5")


def test_docker_run_postgres_with_driver_pg8000():
    postgres_container = PostgresContainer("postgres:9.5", driver="pg8000")
    with postgres_container as postgres:
        engine = sqlalchemy.create_engine(postgres.get_connection_url())
        with engine.begin() as connection:
            connection.execute(sqlalchemy.text("select 1=1"))


# This is a feature in the generic DbContainer class
# but it can't be tested on its own
# so is tested in various database modules:
# - mysql / mariadb
# - postgresql
# - sqlserver
# - mongodb
def test_quoted_password():
    user = "root"
    password = "p@$%25+0&%rd :/!=?"
    quoted_password = "p%40%24%2525+0%26%25rd %3A%2F%21%3D%3F"
    driver = "psycopg2"
    port = 5432
    expected_url = f"postgresql+{driver}://{user}:{quoted_password}@localhost:{port}/test"
    kwargs = {
        "driver": driver,
        "username": user,
        "password": password,
    }
    with PostgresContainer("postgres:16", **kwargs).with_bind_ports(port, port) as container:
        url = container.get_connection_url()
        assert url == expected_url
