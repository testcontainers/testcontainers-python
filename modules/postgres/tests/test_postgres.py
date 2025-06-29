from pathlib import Path

import pytest
import sqlalchemy

from testcontainers.postgres import PostgresContainer


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


@pytest.mark.inside_docker_check
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


def test_password_with_quotes():
    postgres_container = PostgresContainer("postgres:9.5", password="'''''")
    with postgres_container as postgres:
        engine = sqlalchemy.create_engine(postgres.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("select version()"))
            for row in result:
                assert row[0].lower().startswith("postgresql 9.5")


# This is a feature in the generic DbContainer class
# but it can't be tested on its own
# so is tested in various database modules:
# - mysql / mariadb
# - postgresql
# - sqlserver
# - mongodb
# - db2
def test_quoted_password():
    user = "root"
    password = "p@$%25+0&%rd :/!=?"
    quoted_password = "p%40%24%2525+0%26%25rd %3A%2F%21%3D%3F"
    driver = "psycopg2"
    kwargs = {
        "driver": driver,
        "username": user,
        "password": password,
    }
    with PostgresContainer("postgres:16-alpine", **kwargs) as container:
        port = container.get_exposed_port(5432)
        host = container.get_container_host_ip()
        expected_url = f"postgresql+{driver}://{user}:{quoted_password}@{host}:{port}/test"

        url = container.get_connection_url()
        assert url == expected_url

        with sqlalchemy.create_engine(expected_url).begin() as connection:
            connection.execute(sqlalchemy.text("select 1=1"))

        raw_pass_url = f"postgresql+{driver}://{user}:{password}@{host}:{port}/test"
        with pytest.raises(Exception):
            # it raises ValueError, but auth (OperationalError) = more interesting
            with sqlalchemy.create_engine(raw_pass_url).begin() as connection:
                connection.execute(sqlalchemy.text("select 1=1"))


def test_show_how_to_initialize_db_via_initdb_dir():
    postgres_container = PostgresContainer("postgres:16-alpine")
    script = Path(__file__).parent / "fixtures" / "postgres_create_example_table.sql"
    postgres_container.with_volume_mapping(host=str(script), container=f"/docker-entrypoint-initdb.d/{script.name}")

    insert_query = "insert into example(name, description) VALUES ('sally', 'sells seashells');"
    select_query = "select id, name, description from example;"

    with postgres_container as postgres:
        engine = sqlalchemy.create_engine(postgres.get_connection_url())
        with engine.begin() as connection:
            connection.execute(sqlalchemy.text(insert_query))
            result = connection.execute(sqlalchemy.text(select_query))
            result = result.fetchall()
            assert len(result) == 1
            assert result[0] == (1, "sally", "sells seashells")


def test_none_driver_urls():
    user = "root"
    password = "pass"
    kwargs = {
        "username": user,
        "password": password,
    }
    with PostgresContainer("postgres:16-alpine", driver=None, **kwargs) as container:
        port = container.get_exposed_port(5432)
        host = container.get_container_host_ip()
        expected_url = f"postgresql://{user}:{password}@{host}:{port}/test"

        url = container.get_connection_url()
        assert url == expected_url

    with PostgresContainer("postgres:16-alpine", **kwargs) as container:
        port = container.get_exposed_port(5432)
        host = container.get_container_host_ip()
        expected_url = f"postgresql://{user}:{password}@{host}:{port}/test"

        url = container.get_connection_url(driver=None)
        assert url == expected_url


def test_psycopg_versions():
    """Test that both psycopg2 and psycopg (v2 and v3) work with the container."""

    postgres_container = PostgresContainer("postgres:16-alpine", driver="psycopg2")
    with postgres_container as postgres:
        engine = sqlalchemy.create_engine(postgres.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT 1 as test"))
            assert result.scalar() == 1

    postgres_container = PostgresContainer("postgres:16-alpine", driver="psycopg")
    with postgres_container as postgres:
        engine = sqlalchemy.create_engine(postgres.get_connection_url())
        with engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT 1 as test"))
            assert result.scalar() == 1
