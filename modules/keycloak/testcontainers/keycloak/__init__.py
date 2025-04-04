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

_DEFAULT_DEV_COMMAND = "start-dev"
# Since Keycloak v26.0.0
# See: https://www.keycloak.org/server/all-config#category-bootstrap_admin
ADMIN_USERNAME_ENVIRONMENT_VARIABLE = "KC_BOOTSTRAP_ADMIN_USERNAME"
ADMIN_PASSWORD_ENVIRONMENT_VARIABLE = "KC_BOOTSTRAP_ADMIN_PASSWORD"


class KeycloakContainer(DockerContainer):
    has_realm_imports = False

    """
    Keycloak container.

    Example:

        .. doctest::

            >>> from testcontainers.keycloak import KeycloakContainer

            >>> with KeycloakContainer(f"quay.io/keycloak/keycloak:25.0.4") as keycloak:
            ...     keycloak.get_client().users_count()
            1
    """

    def __init__(
        self,
        image="quay.io/keycloak/keycloak:latest",
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 8080,
        management_port: int = 9000,
        cmd: Optional[str] = _DEFAULT_DEV_COMMAND,
    ) -> None:
        super().__init__(image=image)
        self.username = username or os.environ.get("KEYCLOAK_ADMIN", "test")
        self.password = password or os.environ.get("KEYCLOAK_ADMIN_PASSWORD", "test")
        self.port = port
        self.management_port = management_port
        self.with_exposed_ports(self.port, self.management_port)
        self.cmd = cmd

    def _configure(self) -> None:
        self.with_env(ADMIN_USERNAME_ENVIRONMENT_VARIABLE, self.username)
        self.with_env(ADMIN_PASSWORD_ENVIRONMENT_VARIABLE, self.password)
        # legacy env vars (<= 26.0.0)
        self.with_env("KEYCLOAK_ADMIN", self.username)
        self.with_env("KEYCLOAK_ADMIN_PASSWORD", self.password)
        # Enable health checks
        # see: https://www.keycloak.org/server/health#_relevant_options
        self.with_env("KC_HEALTH_ENABLED", "true")
        # Start Keycloak in development mode
        # see: https://www.keycloak.org/server/configuration#_starting_keycloak_in_development_mode
        if self.has_realm_imports:
            self.cmd += " --import-realm"
        self.with_command(self.cmd)

    def get_url(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"http://{host}:{port}"

    def get_management_url(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.management_port)
        return f"http://{host}:{port}"

    @wait_container_is_ready(requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout)
    def _readiness_probe(self) -> None:
        # Keycloak provides REST API endpoints for health checks: https://www.keycloak.org/server/health
        try:
            # Try the new health endpoint for keycloak 25.0.0 and above
            # See https://www.keycloak.org/docs/25.0.0/release_notes/#management-port-for-metrics-and-health-endpoints
            response = requests.get(f"{self.get_management_url()}/health/ready", timeout=1)
        except requests.exceptions.ConnectionError:
            response = requests.get(f"{self.get_url()}/health/ready", timeout=1)
        response.raise_for_status()
        if _DEFAULT_DEV_COMMAND in self._command:
            wait_for_logs(self, "started in \\d+\\.\\d+s")
            wait_for_logs(self, "Created temporary admin user|Added user '")

    def start(self) -> "KeycloakContainer":
        super().start()
        self._readiness_probe()
        return self

    def with_realm_import_file(self, realm_import_file: str) -> "KeycloakContainer":
        file = os.path.abspath(realm_import_file)
        if not os.path.exists(file):
            raise FileNotFoundError(f"Realm file {file} does not exist")
        self.with_volume_mapping(file, "/opt/keycloak/data/import/realm.json")
        self.has_realm_imports = True
        return self

    def with_realm_import_folder(self, realm_import_folder: str) -> "KeycloakContainer":
        folder = os.path.abspath(realm_import_folder)
        if not os.path.exists(folder):
            raise FileNotFoundError(f"Realm folder {folder} does not exist")
        self.with_volume_mapping(folder, "/opt/keycloak/data/import/")
        self.has_realm_imports = True
        return self

    def get_client(self, **kwargs) -> KeycloakAdmin:
        default_kwargs = {
            "server_url": self.get_url(),
            "username": self.username,
            "password": self.password,
            "realm_name": "master",
            "verify": True,
        }
        kwargs = {**default_kwargs, **kwargs}
        return KeycloakAdmin(**kwargs)
