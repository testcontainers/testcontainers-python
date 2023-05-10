import clickhouse_connect
import clickhouse_driver
from testcontainers.clickhouse import ClickHouseContainer


def test_clickhouse_tcp_interface():
    with ClickHouseContainer() as clickhouse:
        client = clickhouse_driver.Client.from_url(clickhouse.get_connection_url())
        result = client.execute("select 'working'")
        assert result == [("working",)]


def test_clickhouse_http_interface():
    with ClickHouseContainer(port=8123) as clickhouse:
        client = clickhouse_connect.get_client(dsn=clickhouse.get_connection_url())
        result = client.query("select 'working'").result_rows
        assert result == [("working",)]
