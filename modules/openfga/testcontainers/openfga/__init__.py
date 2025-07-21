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

import requests

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready

no_client = False
try:
    from openfga_sdk import ClientConfiguration
    from openfga_sdk.credentials import CredentialConfiguration, Credentials
    from openfga_sdk.sync import OpenFgaClient
except ImportError:
    no_client = True

    class OpenFgaClient:
        pass


_DEFAULT_RUN_COMMAND = "run"


class OpenFGAContainer(DockerContainer):
    """
    OpenFGAContainer container.

    Example:

        .. doctest::

            >>> from testcontainers.openfga import OpenFGAContainer
            >>> from sys import version_info

            >>> with OpenFGAContainer("openfga/openfga:v1.8.4") as openfga:
            ...     {"continuation_token": "", 'stores': []} if version_info < (3, 10) else openfga.get_client().list_stores()
            {'continuation_token': '', 'stores': []}
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        image: str = "openfga/openfga:latest",
        preshared_keys: Optional[list[str]] = None,
        playground_port: int = 3000,
        http_port: int = 8080,
        grpc_port: int = 8081,
        cmd: str = _DEFAULT_RUN_COMMAND,
    ) -> None:
        super().__init__(image=image)
        self.preshared_keys = preshared_keys
        self.playground_port = playground_port
        self.http_port = http_port
        self.grpc_port = grpc_port
        self.with_exposed_ports(self.playground_port, self.http_port, self.grpc_port)
        self.cmd = cmd

    def _configure(self) -> None:
        if self.preshared_keys:
            self.cmd += " --authn-method=preshared"
            self.cmd += f' --authn-preshared-keys="{",".join(self.preshared_keys)}"'
        self.with_command(self.cmd)

    def get_api_url(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.http_port)
        return f"http://{host}:{port}"

    @wait_container_is_ready(requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout)
    def _readiness_probe(self) -> None:
        self.exec(["grpc_health_probe", "-addr=0.0.0.0:8081"])  # from chart

    def start(self) -> "OpenFGAContainer":
        super().start()
        self._readiness_probe()
        return self

    def get_preshared_keys(self) -> Optional[list[str]]:
        return self.preshared_keys

    def get_client(self) -> "OpenFgaClient":
        if no_client:
            raise NotImplementedError("failed to import openfga_sdk: is python < 3.10?")

        credentials = None
        if preshared_keys := self.get_preshared_keys():
            credentials = Credentials(
                method="api_token",
                configuration=CredentialConfiguration(
                    api_token=preshared_keys[0],
                ),
            )
        client_configuration = ClientConfiguration(api_url=self.get_api_url(), credentials=credentials)
        return OpenFgaClient(client_configuration)
