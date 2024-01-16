#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from datetime import datetime
from typing import Type

from influxdb.resultset import ResultSet
from influxdb_client import Bucket
from influxdb_client.client.write_api import SYNCHRONOUS
from pytest import mark

from testcontainers.influxdb import InfluxDbContainer
from testcontainers.influxdb1 import InfluxDb1Container
from testcontainers.influxdb2 import InfluxDb2Container


@mark.parametrize(
    ["image", "influxdb_container_class", "exposed_port"], [
        ("influxdb:2.7", InfluxDb1Container, 8086),
        ("influxdb:1.8", InfluxDb2Container, 8086),
    ]
)
def test_influxdbcontainer_get_url(image : str, influxdb_container_class: Type[InfluxDbContainer], exposed_port: int):
    with influxdb_container_class(image, host_port=exposed_port) as influxdb_container:
        connection_url = influxdb_container.get_url()
        assert str(exposed_port) in connection_url

@mark.parametrize(
    ["image", "influxdb_container_class", "expected_version"], [
        ("influxdb:1.8", InfluxDb1Container, "1.8.10"),
        ("influxdb:1.8.10", InfluxDb1Container, "1.8.10"),
        ("influxdb:2.7", InfluxDb2Container, "v2.7.4"),
        ("influxdb:2.7.4", InfluxDb2Container, "v2.7.4"),
    ]
)
def test_influxdbcontainer_get_influxdb_version(image: str, influxdb_container_class: Type[InfluxDbContainer], expected_version: str):
    with influxdb_container_class(image) as influxdb_container:
        assert influxdb_container.get_influxdb_version() == expected_version

def test_influxdb1container_get_client():
    """
    This is a test example showing how you could use testcontainers/influxdb for InfluxDB 1.x versions
    """
    with InfluxDb1Container("influxdb:1.8") as influxdb1_container:
        influxdb1_client = influxdb1_container.get_client()
        databases = influxdb1_client.get_list_database()
        assert len(databases) == 0, "the InfluxDB container starts with no database at all"

        # creates a database and inserts some datapoints
        influxdb1_client.create_database("testcontainers")
        databases = influxdb1_client.get_list_database()
        assert len(databases) == 1, "the InfluxDB container now contains one database"
        assert databases[0] == {"name": "testcontainers"}
        
        influxdb1_client.write_points([
            {
                "measurement": "influxdbcontainer",
                "time": "1978-11-30T09:30:00Z",
                "fields": {
                    "ratio": 0.42
                }
            }, {
                "measurement": "influxdbcontainer",
                "time": "1978-12-25T10:30:00Z",
                "fields": {
                    "ratio": 0.55
                }
            },
        ], database="testcontainers")

        # retrieves the inserted datapoints
        datapoints_set: ResultSet = influxdb1_client.query("select ratio from influxdbcontainer;", database="testcontainers")
        datapoints = list(datapoints_set.get_points())
        assert len(datapoints) == 2, '2 datapoints are retrieved'

        datapoint = datapoints[0]
        assert datapoint['time'] == "1978-11-30T09:30:00Z"
        assert datapoint['ratio'] == 0.42

        datapoint = datapoints[1]
        assert datapoint['time'] == "1978-12-25T10:30:00Z"
        assert datapoint['ratio'] == 0.55
      

def test_influxdb2container_get_client():
    """
    This is a test example showing how you could use testcontainers/influxdb for InfluxDB 2.x versions with the Flux query language
    """
    with InfluxDb2Container(
        "influxdb:2.7",
        init_mode="setup",
        username="root",
        password="secret-password",
        org_name="testcontainers-org",
        bucket="my-init-bucket",
        admin_token="secret-token"
    ) as influxdb2_container:
        influxdb2_client, test_org = influxdb2_container.get_client(token="secret-token", org_name="testcontainers-org")
        assert influxdb2_client.ping(), "the client can connect to the InfluxDB instance"

        # ensures that the bucket does not exist yet
        buckets_api = influxdb2_client.buckets_api()
        bucket: Bucket = buckets_api.find_bucket_by_name("testcontainers")
        assert bucket is None, 'the test bucket does not exist yet'

        # creates a test bucket and insert a point
        buckets_api.create_bucket(bucket_name="testcontainers", org=test_org)
        bucket: Bucket = buckets_api.find_bucket_by_name("testcontainers")
        assert bucket.name == "testcontainers", 'the test bucket now exists'

        write_api = influxdb2_client.write_api(write_options=SYNCHRONOUS)
        write_api.write("testcontainers", "testcontainers-org", [
            {
                "measurement": "influxdbcontainer",
                "time": "1978-11-30T09:30:00Z",
                "fields": {
                    "ratio": 0.42
                }
            }, {
                "measurement": "influxdbcontainer",
                "time": "1978-12-25T10:30:00Z",
                "fields": {
                    "ratio": 0.55
                }
            },
        ])

        # retrieves the inserted datapoints
        query_api = influxdb2_client.query_api()
        tables = query_api.query('from(bucket: "testcontainers") |> range(start: 1978-11-01T22:00:00Z)', org=test_org)
        results = tables.to_values(['_measurement', '_field', '_time', '_value'])
        
        assert len(results) == 2, '2 datapoints were retrieved'
        assert results[0] == ['influxdbcontainer', 'ratio', datetime.fromisoformat('1978-11-30T09:30:00+00:00'), 0.42]
        assert results[1] == ['influxdbcontainer', 'ratio', datetime.fromisoformat('1978-12-25T10:30:00+00:00'), 0.55]
