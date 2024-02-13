import clickhouse_driver

from testcontainers.clickhouse import ClickHouseContainer


def test_docker_run_clickhouse():
    clickhouse_container = ClickHouseContainer()
    with clickhouse_container as clickhouse:
        client = clickhouse_driver.Client.from_url(clickhouse.get_connection_url())
        result = client.execute("select 'working'")

        assert result == [("working",)]
