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
from typing import Optional

import requests
from keycloak import KeycloakAdmin
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class KeycloakContainer(DockerContainer):
    """
        Keycloak container.

        Example:

            .. doctest::

                >>> from testcontainers.keycloak import KeycloakContainer

                >>> with KeycloakContainer() as kc:
                ...    keycloak = kc.get_client()
    """
    def __init__(
            self,
            image="quay.io/keycloak/keycloak:latest",
            username: Optional[str] = None,
            password: Optional[str] = None,
            port: int = 8080
    ) -> None:
        super(KeycloakContainer, self).__init__(image=image)
        self.username = username or os.getenv("KEYCLOAK_ADMIN", "test")
        self.password = password or os.getenv("KEYCLOAK_ADMIN_PASSWORD", "test")
        self.port = port
        self.with_exposed_ports(self.port)

    def _get_image_tag(self) -> str:
        return self.image.split(":")[1]

    def _uses_legacy_architecture(self) -> bool:
        tag = self._get_image_tag()

        try:
            major_version_number = int(tag.split(".")[0])
        except ValueError:
            major_version_number = 2023

        return major_version_number <= 16 or "legacy" in tag.lower()

    def _configure(self) -> None:
        # There's a bit of confusion as to which version / architecture uses which
        # Because of this we're setting the credentials both ways
        self.with_env("KEYCLOAK_ADMIN", self.username)
        self.with_env("KEYCLOAK_ADMIN_PASSWORD", self.password)
        self.with_env("KEYCLOAK_USER", self.username)
        self.with_env("KEYCLOAK_PASSWORD", self.password)

        self.with_env("KC_HEALTH_ENABLED", "true")
        self.with_env("KC_METRICS_ENABLED", "true")

        if not self._uses_legacy_architecture():
            self.with_command("start-dev")

    def get_url(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"http://{host}:{port}"

    def get_base_api_url(self) -> str:
        base_url = self.get_url()
        return f"{base_url}/auth" if self._uses_legacy_architecture() else base_url

    @wait_container_is_ready(requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout)
    def _connect(self) -> None:
        url = self.get_url()
        response = requests.get(f"{url}/auth", timeout=1)
        response.raise_for_status()

    def start(self) -> "KeycloakContainer":
        self._configure()
        container = super().start()

        if self._uses_legacy_architecture():
            self._connect()
        else:
            wait_for_logs(container, 'Listening on:')

        return self

    def get_client(self, **kwargs) -> KeycloakAdmin:
        return KeycloakAdmin(
            server_url=f"{self.get_base_api_url()}/",
            username=self.username,
            password=self.password,
            verify=True
        )
