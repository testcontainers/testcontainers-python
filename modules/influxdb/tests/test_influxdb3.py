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

from testcontainers.influxdb3 import InfluxDb3Container


def test_influxdb3_container_starts_with_auth():
    with InfluxDb3Container("influxdb:3-core") as container:
        token = container.token
        assert token is not None, "Token should be generated when auth is enabled"
        assert token.startswith("apiv3_"), "Token should start with apiv3_"


def test_influxdb3_container_starts_without_auth():
    with InfluxDb3Container("influxdb:3-core", is_auth_disabled=True) as container:
        token = container.token
        assert token is None, "Token should be None when auth is disabled"


def test_influxdb3_container_get_url():
    with InfluxDb3Container("influxdb:3-core", host_port=8181) as container:
        url = container.get_url()
        assert "8181" in url, "URL should contain the exposed port"
        assert url.startswith("http://"), "URL should start with http://"


def test_influxdb3_write_and_query_data():
    with InfluxDb3Container("influxdb:3-core") as container:
        client = container.get_client(database="test1")

        client.write("temperature,location=west value=55.15")

        query = "SELECT time, location, value FROM temperature"
        table = client.query(query=query, language="sql")
        rows = table.to_pylist()

        assert len(rows) == 1, "Should have retrieved 1 row"
        assert rows[0]["location"] == "west"
        assert rows[0]["value"] == 55.15

        client.close()


def test_influxdb3_write_and_query_data_no_auth():
    with InfluxDb3Container("influxdb:3-core", is_auth_disabled=True) as container:
        client = container.get_client(database="test2")

        client.write("humidity,location=east value=72.3")

        query = "SELECT time, location, value FROM humidity"
        table = client.query(query=query, language="sql")
        rows = table.to_pylist()

        assert len(rows) == 1, "Should have retrieved 1 row"
        assert rows[0]["location"] == "east"
        assert rows[0]["value"] == 72.3

        client.close()
