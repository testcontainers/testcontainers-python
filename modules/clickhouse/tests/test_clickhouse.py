import pytest

from clickhouse_driver import Client

from testcontainers.clickhouse import ClickHouseContainer


def test_docker_run_clickhouse():
    with ClickHouseContainer(f"clickhouse/clickhouse-server:24.3.1-alpine") as clickhouse:
        client = Client.from_url(clickhouse.get_connection_url())
        result = client.execute("select 'working'")

        assert result == [("working",)]
