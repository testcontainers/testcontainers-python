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

from http.client import HTTPException
from urllib.request import urlopen

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class VaultContainer(DockerContainer):
    """
    Vault container.

    Example:

        .. doctest::

            >>> from testcontainers.vault import VaultContainer
            >>> import hvac

            >>> with VaultContainer("hashicorp/vault:1.16.1") as vault_container:
            ...     connection_url = vault_container.get_connection_url()
            ...     client = hvac.Client(url=connection_url, token=vault_container.root_token)
            ...     assert client.is_authenticated()
            ...     # use root client to perform desired actions, e.g.
            ...     policies = client.sys.list_acl_policies()
    """

    def __init__(
        self,
        image: str = "hashicorp/vault:latest",
        port: int = 8200,
        root_token: str = "toor",
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)
        self.port = port
        self.root_token = root_token
        self.with_exposed_ports(self.port)
        self.with_env("VAULT_DEV_ROOT_TOKEN_ID", self.root_token)

    def get_connection_url(self) -> str:
        """
        Get the connection URL used to connect to the Vault container.

        Returns:
            str: The address to connect to.
        """
        host_ip = self.get_container_host_ip()
        exposed_port = self.get_exposed_port(self.port)
        return f"http://{host_ip}:{exposed_port}"

    @wait_container_is_ready(HTTPException)
    def _healthcheck(self) -> None:
        url = f"{self.get_connection_url()}/v1/sys/health"
        with urlopen(url) as res:
            if res.status > 299:
                raise HTTPException()

    def start(self) -> "VaultContainer":
        super().start()
        self._healthcheck()
        return self
