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
import os
import requests

from keycloak import KeycloakAdmin

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class KeycloakContainer(DockerContainer):
    """
    Keycloak container.

    Example
    -------
    .. doctest::

        >>> from testcontainers.keycloak import KeycloakContainer

        >>> with KeycloakContainer() as kc:
        ...    keycloak = kc.get_client()
    """
    KEYCLOAK_USER = os.environ.get("KEYCLOAK_USER", "test")
    KEYCLOAK_PASSWORD = os.environ.get("KEYCLOAK_PASSWORD", "test")

    def __init__(self, image="jboss/keycloak:latest"):
        super(KeycloakContainer, self).__init__(image=image)
        self.port_to_expose = 8080
        self.with_exposed_ports(self.port_to_expose)

    def _configure(self):
        self.with_env("KEYCLOAK_USER", self.KEYCLOAK_USER)
        self.with_env("KEYCLOAK_PASSWORD", self.KEYCLOAK_PASSWORD)

    def get_url(self):
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port_to_expose)
        return "http://{}:{}".format(host, port)

    @wait_container_is_ready(requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout)
    def _connect(self):
        url = self.get_url()
        response = requests.get("{}/auth".format(url), timeout=1)
        response.raise_for_status()

    def start(self):
        self._configure()
        super().start()
        self._connect()
        return self

    def get_client(self, **kwargs):
        default_kwargs = dict(
            server_url="{}/auth/".format(self.get_url()),
            username=self.KEYCLOAK_USER,
            password=self.KEYCLOAK_PASSWORD,
            realm_name="master",
            verify=True,
        )
        kwargs = {
            **default_kwargs,
            **kwargs
        }
        return KeycloakAdmin(**kwargs)
