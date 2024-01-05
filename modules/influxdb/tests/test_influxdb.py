from pytest import mark

from testcontainers.influxdb import InfluxDbContainer

@mark.parametrize(
    ["image", "exposed_port"], [
        ("influxdb:2.7", 8086),
        ("influxdb:1.8", 8086),
    ]
)
def test_influxdbcontainer(image : str, exposed_port: int):
    with InfluxDbContainer(image, host_port=exposed_port) as influxdb_container:
        connection_url = influxdb_container.get_url()
        assert str(exposed_port) in connection_url

@mark.parametrize(
    ["image", "expected_version"], [
        ("influxdb:1.8", "1.8.10"),
        ("influxdb:1.8.10", "1.8.10"),
        ("influxdb:2.7", "v2.7.4"),
        ("influxdb:2.7.4", "v2.7.4"),
    ]
)
def test_get_version(image: str, expected_version: str):
    with InfluxDbContainer(image) as influxdb_container:
        assert influxdb_container.get_influxdb_version() == expected_version
