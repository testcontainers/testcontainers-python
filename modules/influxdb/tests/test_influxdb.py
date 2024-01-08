from influxdb.resultset import ResultSet
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

def test_get_client_v1():
    with InfluxDbContainer("influxdb:1.8") as influxdb_container:
        client_v1 = influxdb_container.get_client_v1()
        databases = client_v1.get_list_database()
        assert len(databases) == 0, "the InfluxDB container starts with no database at all"

        # creates a database and inserts some datapoints
        client_v1.create_database("testcontainers")
        databases = client_v1.get_list_database()
        assert len(databases) == 1, "the InfluxDB container now contains one database"
        assert databases[0] == {"name": "testcontainers"}
        
        client_v1.write_points([
            {
                "measurement": "influxdbcontainer",
                "time": "1978-11-30T09:30:00Z",
                "fields": {
                    "value": 0.42
                }
            }
        ], database="testcontainers")

        # retrieves the inserted datapoint
        datapoints_set: ResultSet = client_v1.query("select value from influxdbcontainer;", database="testcontainers")
        datapoints = list(datapoints_set.get_points())
        assert len(datapoints) == 1, 'retrieved the inserted point'

        datapoint = datapoints[0]
        assert datapoint['time'] == "1978-11-30T09:30:00Z"
        assert datapoint['value'] == 0.42
