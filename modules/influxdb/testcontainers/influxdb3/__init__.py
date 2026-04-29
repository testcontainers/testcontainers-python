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
from typing import TYPE_CHECKING, Optional, override

import requests

from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy

if TYPE_CHECKING:
    from influxdb_client_3 import InfluxDBClient3


class InfluxDb3Container(DockerContainer):
    """
    Docker container for InfluxDB 3 Core.
    Official Docker images for InfluxDB are hosted at https://hub.docker.com/_/influxdb/.

    Example:

        .. doctest::

            >>> from testcontainers.influxdb3 import InfluxDb3Container

            >>> with InfluxDb3Container() as influxdb3:
            ...    url = influxdb3.get_url()
    """

    INFLUXDB3_PORT = 8181

    def __init__(
        self,
        image: str = "influxdb:3-core",
        container_port: int = INFLUXDB3_PORT,
        host_port: Optional[int] = None,
        is_auth_disabled: bool = False,
        **kw,
    ):
        """
        Initialize InfluxDB 3 container.

        Args:
            image: Docker image to use. Defaults to ``influxdb:3-core``.
            container_port: Port inside the container. Defaults to ``8181``.
            host_port: Port on the host to bind to. If ``None``, a random port is assigned.
            is_auth_disabled: If ``True``, disables authentication. Defaults to ``False``.
            **kw: Additional keyword arguments passed to ``DockerContainer``.
        """
        super().__init__(image=image, **kw)

        self.container_port: int = container_port
        self.host_port: Optional[int] = host_port
        _ = self.with_bind_ports(self.container_port, self.host_port)

        self._is_auth_disabled: bool = is_auth_disabled
        self.token: Optional[str] = None

        _ = self.with_command(
            "influxdb3 serve --node-id local01 --object-store file --data-dir /home/influxdb3/.influxdb3"
        )

        if self._is_auth_disabled:
            healthy_status_code = 200
            _ = self.with_env("INFLUXDB3_START_WITHOUT_AUTH", str(self._is_auth_disabled).lower())
        else:
            healthy_status_code = 401

        _ = self.waiting_for(HttpWaitStrategy(self.container_port, "/health").for_status_code(healthy_status_code))

    def get_url(self) -> str:
        """
        Get the URL to connect to the InfluxDB 3 instance.

        Returns:
            The HTTP URL of the running InfluxDB 3 container.
        """
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.container_port)
        return f"http://{host}:{port}"

    def _create_token(self) -> str:
        url = f"{self.get_url()}/api/v3/configure/token/admin"
        response = requests.post(
            url, headers={"Accept": "application/json", "Content-Type": "application/json"}, timeout=10
        )
        response.raise_for_status()
        return response.json()["token"]

    def get_client(self, database: str, **kw) -> "InfluxDBClient3":
        """
        Get an InfluxDB 3 client connected to this container.

        Args:
            database: Database name to connect to.
            **kw: Additional keyword arguments passed to ``InfluxDBClient3``.

        Returns:
            An ``InfluxDBClient3`` instance connected to this container.
        """
        from influxdb_client_3 import InfluxDBClient3

        return InfluxDBClient3(
            host=self.get_url(),
            token=self.token,
            database=database,
            **kw,
        )

    @override
    def start(self) -> "InfluxDb3Container":
        """
        Start the InfluxDB 3 container and initialize authentication.

        Returns:
            The started ``InfluxDb3Container`` instance.
        """
        _ = super().start()
        if not self._is_auth_disabled:
            self.token = self._create_token()
        return self
