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

from typing import Optional

from influxdb import InfluxDBClient

from testcontainers.influxdb import InfluxDbContainer


class InfluxDb1Container(InfluxDbContainer):
    """
    Docker container for InfluxDB 1.x.
    Official Docker images for InfluxDB are hosted at https://hub.docker.com/_/influxdb/.

    Example:

        .. doctest::

            >>> from testcontainers.influxdb1 import InfluxDbContainer

            >>> with InfluxDbContainer() as influxdb:
            ...    version = influxdb.get_version()
    """

    def __init__(
        self,
        image: str = "influxdb:1.8",
        # in the container, the default port for influxdb is often 8086 and not likely to change
        container_port: int = 8086,
        # specifies the port on the host machine where influxdb is exposed; a random available port otherwise
        host_port: Optional[int] = None,
        **docker_client_kw,
    ):
        super().__init__(image, container_port, host_port, **docker_client_kw)

    def get_client(self, **client_kwargs):
        """
        Returns an instance of the influxdb client, for InfluxDB 1.x versions.
        Note that this client is not maintained anymore, but it is the only
        official client available for 1.x InfluxDB versions:
        - https://github.com/influxdata/influxdb-python
        - https://pypi.org/project/influxdb/

        To some extent, you can use the v2 client with InfluxDB v1.8+:
        - https://github.com/influxdata/influxdb-client-python#influxdb-18-api-compatibility
        """

        return InfluxDBClient(self.get_container_host_ip(), self.get_exposed_port(self.container_port), **client_kwargs)

    def start(self) -> "InfluxDb1Container":
        """
        Overridden for better typing reason
        """
        return super().start()
