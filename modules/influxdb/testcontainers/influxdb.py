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

"""
testcontainers/influxdb provides means to spawn an InfluxDB instance within a Docker container.

- this influxdb.py module provides the common mechanism to spawn an InfluxDB container.
  You are not likely to use this module directly.
- import the InfluxDb1Container class from the influxdb1/__init__.py module to spawn
  a container for an InfluxDB 1.x instance
- import the InfluxDb2Container class from the influxdb2/__init__.py module to spawn
  a container for an InfluxDB 2.x instance

The 2 containers are separated in different modules for 2 reasons:
- because the Docker images are not designed to be used in the same way
- because the InfluxDB clients are different for 1.x and 2.x versions,
  so you won't have to install dependencies that you do not need
"""
from typing import Optional

from typing_extensions import override

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import create_connection_string
from testcontainers.core.waiting_utils import wait_for_http


class InfluxDbContainer(DockerContainer):
    """
    Abstract class for Docker containers of InfluxDB v1 and v2.

    Concrete implementations for InfluxDB 1.x and 2.x are separated iun different packages
    because their respective clients rely on different Python libraries which we don't want
    to import at the same time.
    """

    def __init__(
        self,
        # Docker image name
        image: str,
        # in the container, the default port for influxdb is often 8086 and not likely to change
        container_port: int = 8086,
        # specifies the port on the host machine where influxdb is exposed; a random available port otherwise
        host_port: Optional[int] = None,
        **docker_client_kw,
    ):
        super().__init__(image=image, **docker_client_kw)
        self.container_port = container_port
        self.host_port = host_port
        self.with_bind_ports(self.container_port, self.host_port)

    def get_url(self) -> str:
        return create_connection_string(
            dialect="http", host=self.get_container_host_ip(), port=self.get_exposed_port(self.container_port)
        )

    @override
    def _wait_until_ready(self) -> None:
        wait_for_http(f"{self.get_url()}/health")
