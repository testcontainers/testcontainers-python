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

import hvac
from urllib.request import urlopen
from http.client import HTTPException
from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready


class VaultContainer(DockerContainer):
    """
    Vault container.

    Example:

        .. doctest::

            >>> from testcontainers.vault import VaultContainer

            >>> with VaultContainer("hashicorp/vault:1.16.1") as vault_container:
            ...     vault_client = vault_container.get_client()
    """
    def __init__(self, image: str = "hashicorp/vault:latest", port: int = 8200,
                 root_token: str = "toor", **kwargs) -> None:
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super(VaultContainer, self).__init__(image, **kwargs)
        self.port = port
        self.root_token = root_token
        self.with_exposed_ports(self.port)
        self.with_env("VAULT_DEV_ROOT_TOKEN_ID", self.root_token)

    def get_config(self) -> dict:
        """
        Get the configuration used to connect to the Vault container, including the address to
        connect to, and the root token.

        Returns:
            dict: {`address`: str, `root_token`: str}
        """
        host_ip = self.get_container_host_ip()
        exposed_port = self.get_exposed_port(self.port)
        return {
            "root_token": self.root_token,
            "address": f"http://{host_ip}:{exposed_port}",
        }

    def get_client(self) -> hvac.Client:
        """
        Get a Vault client.

        Returns:
            client: Vault client to connect to the container.
        """
        config = self.get_config()
        return hvac.Client(url=config["address"])

    def get_root_client(self) -> hvac.Client:
        """
        Get an authenticated Vault client with root token.

        Returns:
            client: Vault client to connect to the container.
        """
        config = self.get_config()
        return hvac.Client(url=config["address"], token=config["root_token"])

    @wait_container_is_ready(HTTPException)
    def _healthcheck(self) -> None:
        url = f"{self.get_config()['address']}/v1/sys/health"
        with urlopen(url) as res:
            if res.status > 299:
                raise HTTPException()

    def start(self) -> "VaultContainer":
        super().start()
        self._healthcheck()
        return self
