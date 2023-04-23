import clickhouse_driver
import pytest
from testcontainers.clickhouse import ClickHouseContainer


def test_docker_run_clickhouse():
    with ClickHouseContainer() as clickhouse:
        client = clickhouse_driver.Client.from_url(clickhouse.get_connection_url())
        result = client.execute("select 'working'")

        assert result == [('working',)]


test_clickhouse_docs = pytest.shared.build_doctests("testcontainers.clickhouse")
