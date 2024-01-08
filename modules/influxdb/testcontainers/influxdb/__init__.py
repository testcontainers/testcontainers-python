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

from os import getenv
from typing import Dict, Optional

from influxdb import InfluxDBClient as InfluxDBClientV1
from requests import get
from requests.exceptions import ConnectionError, ReadTimeout

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class InfluxDbContainer(DockerContainer):
    """
    InfluxDB container.
    Official Docker images for InfluxDB are hosted at https://hub.docker.com/_/influxdb/.

    Example:

        .. doctest::

            >>> from testcontainers.influxdb import InfluxDbContainer

            >>> with InfluxDbContainer() as influxdb:
            ...    version = influxdb.get_version()
    """
    def __init__(
        self,
        image: str = "influxdb:latest",

        # in the container, the default port for influxdb is often 8086 and not likely to change
        container_port: int = 8086,
        # specifies the port on the host machine where influxdb is exposed; a random available port otherwise
        host_port: Optional[int] = None,

        # parameters used by the Docker container. Explicitely set them via the constructor or by their
        # respective environment variables
        username: Optional[str] = None,
        password: Optional[str] = None,
        org: Optional[str] = None,
        bucket: Optional[str] = None,
        retention: Optional[str] = None,
        admin_token: Optional[str] = None,
    ):
        super().__init__(image=image)
        self.container_port = container_port
        self.host_port = host_port
        self.with_bind_ports(self.container_port, self.host_port)

        configuration = {
            "DOCKER_INFLUXDB_INIT_USERNAME": username,
            "DOCKER_INFLUXDB_INIT_PASSWORD": password,
            "DOCKER_INFLUXDB_INIT_ORG": org,
            "DOCKER_INFLUXDB_INIT_BUCKET": bucket,
            "DOCKER_INFLUXDB_INIT_RETENTION": retention,
            "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN": admin_token,
        }
        for env_key, env_param in configuration.items():
            env_value = env_param or getenv(env_key)
            if env_value:
                self.with_env(env_value)

    def get_url(self) -> str:
        """
        Returns the url to interact with the InfluxDB container (health check, REST API, etc.)
        """
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.container_port)

        return f"http://{host}:{port}"

    @wait_container_is_ready(ConnectionError, ReadTimeout)
    def _health_check(self) -> Dict:
        """
        Performs a health check on the running InfluxDB container.
        The call is retried until it works thanks to the @wait_container_is_ready decorator.
        See its documentation for the max number of retries or the timeout.
        """

        url = self.get_url()
        response = get(f"{url}/health", timeout=1)
        response.raise_for_status()

        return response.json()
    
    def get_influxdb_version(self) -> str:
        """
        Returns the version of the InfluxDB service, as returned by the healthcheck.
        """

        return self._health_check().get('version')

    def start(self) -> "InfluxDbContainer":
        super().start()
        self._health_check()

        return self

    def get_client_v1(self, **client_kwargs) -> InfluxDBClientV1:
        """
        Returns an instance of the influxdb client, for InfluxDB 1.x versions.
        Note that this client is not maintained anymore, but it is the only
        official client available for 1.x InfluxDB versions:
        - https://github.com/influxdata/influxdb-python
        - https://pypi.org/project/influxdb/

        To some extent, you can use the v2 client with InfluxDB v1.8+:
        - https://github.com/influxdata/influxdb-client-python#influxdb-18-api-compatibility
        """

        return InfluxDBClientV1(
            self.get_container_host_ip(),
            self.get_exposed_port(self.container_port),
            **client_kwargs
        )
