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
from typing import Optional

from influxdb_client import InfluxDBClient, Organization

from testcontainers.influxdb import InfluxDbContainer


class InfluxDb2Container(InfluxDbContainer):
    """
    Docker container for InfluxDB 2.x.
    Official Docker images for InfluxDB are hosted at https://hub.docker.com/_/influxdb/.

    Example:

        .. doctest::

            >>> from testcontainers.influxdb2 import InfluxDb2Container

            >>> with InfluxDb2Container() as influxdb2:
            ...    version = influxdb2.get_version()
    """

    def __init__(
        self,
        image: str = "influxdb:latest",
        # in the container, the default port for influxdb is often 8086 and not likely to change
        container_port: int = 8086,
        # specifies the port on the host machine where influxdb is exposed; a random available port otherwise
        host_port: Optional[int] = None,
        # parameters used by the InfluxDSB 2.x Docker container when spawned in setup mode
        # (which is likely what you want). In setup mode, init_mode should be "setup" and all
        # the other parameters should be set (via this constructor or their respective
        # environment variables); retention does not need to be explicitely set.
        init_mode: Optional[str] = None,
        admin_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        org_name: Optional[str] = None,
        bucket: Optional[str] = None,
        retention: Optional[str] = None,
        **docker_client_kw,
    ):
        super().__init__(image, container_port, host_port, **docker_client_kw)

        configuration = {
            "DOCKER_INFLUXDB_INIT_MODE": init_mode,
            "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN": admin_token,
            "DOCKER_INFLUXDB_INIT_USERNAME": username,
            "DOCKER_INFLUXDB_INIT_PASSWORD": password,
            "DOCKER_INFLUXDB_INIT_ORG": org_name,
            "DOCKER_INFLUXDB_INIT_BUCKET": bucket,
            "DOCKER_INFLUXDB_INIT_RETENTION": retention,
        }
        for env_key, constructor_param in configuration.items():
            env_value = constructor_param or getenv(env_key)
            if env_value:
                self.with_env(env_key, env_value)

    def start(self) -> "InfluxDb2Container":
        """
        Overridden for better typing reason
        """
        return super().start()

    def get_client(
        self, token: Optional[str] = None, org_name: Optional[str] = None, **influxdb_client_kwargs
    ) -> tuple[InfluxDBClient, Organization]:
        """
        Returns an instance of the influxdb client with the associated test organization created
        when the container is spawn; for InfluxDB 2.x versions.
        - https://github.com/influxdata/influxdb-client-python
        - https://pypi.org/project/influxdb-client/

        This InfluxDB client requires to specify the organization when using most of the API's endpoints,
        as an Organisation instance rather than its name or id (deprecated). As a convenience, this
        client getter can also retrieve and return the organization instance along with the client.
        Otherwise, None is returned in place of the organization instance.

        This organization is created when spawning the container in setup mode (which is likely what you
        want) by giving its name to the 'org_name' parameter constructor.
        """

        influxclient = InfluxDBClient(self.get_url(), token=token, **influxdb_client_kwargs)

        if org_name is None:
            return influxclient, None

        orgs = influxclient.organizations_api().find_organizations(org=org_name)
        if len(orgs) == 0:
            raise ValueError(f"Could not retrieved the Organization corresponding to name '{org_name}'")

        return influxclient, orgs[0]
