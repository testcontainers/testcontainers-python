from asyncio import sleep

import pytest
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer


def test_docker_run_postgres():
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


@pytest.mark.asyncio
async def test_docker_run_postgres_with_driver_asyncio():
    postgres_container = PostgresContainer("postgres:9.5", driver="asyncpg")
    with postgres_container as postgres:
        # in local test need to wait while pg container is ready
        # else raised `ConnectionError: unexpected connection_lost() call`
        await sleep(5)
        engine = create_async_engine(postgres.get_connection_url())
        async with engine.begin() as connection:
            await connection.execute(sqlalchemy.text("select 1=1"))
