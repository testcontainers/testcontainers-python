import threading

import pytest
from risingwave.core import OutputFormat
from sqlalchemy import Row
from testcontainers.risingwave import RisingWaveContainer


@pytest.mark.inside_docker_check
@pytest.mark.parametrize("version", ["v1.10.1", "v1.10.2", "v2.0.2", "latest"])
def test_docker_run_risingwave_versions(version: str):
    with RisingWaveContainer(f"risingwavelabs/risingwave:{version}") as rw:
        client = rw.get_client()
        try:
            result = client.fetchone("select version();")
            assert isinstance(result, Row), "Result is not of type sqlalchemy.Row"
            got_version = result[0]
            assert got_version.startswith("PostgreSQL 13.14.0-RisingWave")
            if version != "latest":
                assert version in version
        finally:
            # close to suppress warnings from OperationalError in between runs.
            client.conn.close()


@pytest.mark.inside_docker_check
def test_docker_run_risingwave_in_parallel():
    PORTS = [4500, 4566]

    def run_risingwave(port):
        with RisingWaveContainer(image="risingwavelabs/risingwave:v2.0.2", port=port) as rw:
            client = rw.get_client()
            try:
                assert rw.port == port
                assert rw.internal_port == 4566
                assert client.conn.closed is False
            finally:
                # close to suppress warnings from OperationalError in between runs.
                client.conn.close()

    for port in PORTS:
        threading.Thread(target=run_risingwave, args=(port,)).start()


@pytest.mark.inside_docker_check
def test_docker_run_risingwave_create_materialized_view():
    import time

    import pandas as pd

    # ARRANGE
    SCHEMA = "testcontainer"
    raw_data = [
        {"id": 1, "name": "Alice", "age": 18},
        {"id": 2, "name": "Bob", "age": 19},
        {"id": 3, "name": "Charlie", "age": 20},
        {"id": 4, "name": "David", "age": 21},
        {"id": 5, "name": "Alice", "age": 22},
    ]
    want_data = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie", "David"],
            "total_age": [40, 19, 20, 21],
            "total_count": [2, 1, 1, 1],
        }
    )

    # ACT
    with RisingWaveContainer() as rw:
        client = rw.get_client()

        def generate_data():
            client.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
            client.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {SCHEMA}.example_table
                (id INT, name TEXT, age INT)
                """
            )
            for rd in raw_data:
                client.insert_row(
                    table_name="example_table",
                    schema_name=SCHEMA,
                    force_flush=True,
                    **rd,
                )
                time.sleep(1)

        def create_mv():
            while not client.check_exist(name="example_table", schema_name=SCHEMA):
                time.sleep(1)
                continue
            return client.mv(
                name="example_mv",
                schema_name=SCHEMA,
                stmt=f"""
                SELECT name, SUM(age) AS total_age, COUNT(*) AS total_count
                FROM {SCHEMA}.example_table
                GROUP BY 1
                """,
            )

        try:
            for fn in [create_mv, generate_data]:
                threading.Thread(target=fn).start()

            time.sleep(len(raw_data) + 2)
            got_data = client.fetch(
                f"select * from {SCHEMA}.example_mv",
                OutputFormat.DATAFRAME,
            )

            # ASSERT
            assert isinstance(got_data, pd.DataFrame)
            pd.testing.assert_frame_equal(
                got_data.sort_values("name").reset_index(drop=True),
                want_data.sort_values("name").reset_index(drop=True),
            )

        finally:
            # close to suppress warnings from OperationalError in between runs.
            client.conn.close()
