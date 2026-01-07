from enum import Enum
from typing import Any, Optional

import requests
from azure.core.credentials import AccessToken, TokenCredential

from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

# This comment can be removed (Used for testing)


class StaticTokenCredential(TokenCredential):
    def __init__(self, json_token: str):
        self.access_token = AccessToken(token=json_token.get("access_token"), expires_on=json_token.get("expires_on"))

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AccessToken:
        return self.access_token


class NetworkType(Enum):
    NETWORK = "network"
    LOCAL = "local"


class LowkeyVaultContainer(DockerContainer):
    """
    Container for a Lowkey Vault instance for emulating Azure Key Vault.

    Example:

        .. doctest::

            >>> from azure.core.pipeline.transport._requests_basic import RequestsTransport
            >>> from azure.keyvault.secrets import SecretClient
            >>> from testcontainers.lowkeyvault import LowkeyVaultContainer

            >>> with LowkeyVaultContainer() as lowkey_vault:
            ...    connection_url = lowkey_vault.get_connection_url()
            ...    token = lowkey_vault.get_token()
            ...    transport = RequestsTransport(connection_verify=False)
            ...    # make sure to turn off challenge resource verification
            ...    secret_client = SecretClient(
            ...        vault_url=connection_url,
            ...        credential=token,
            ...        verify_challenge_resource=False,
            ...        transport=transport
            ...    )
    """

    def __init__(
        self, image: str = "nagyesta/lowkey-vault:7.0.3-ubi10-minimal", container_alias: Optional[str] = None, **kwargs
    ) -> None:
        super().__init__(image, **kwargs)
        self.api_port = 8443
        self.metadata_port = 8080
        self.with_exposed_ports(self.api_port, self.metadata_port)
        self.with_env("LOWKEY_VAULT_RELAXED_PORTS", "true")
        if container_alias is not None:
            self.with_network_aliases(container_alias)
            self.with_env("LOWKEY_VAULT_ALIASES", f"localhost={container_alias}:<port>")
            self.container_alias = container_alias
        self.waiting_for(LogMessageWaitStrategy("Started LowkeyVaultApp."))

    def _configure(self) -> None:
        return

    def get_connection_url(self, network_type: NetworkType = NetworkType.LOCAL) -> str:
        if network_type == NetworkType.LOCAL:
            return f"https://{self.get_container_host_ip()}:{self.get_exposed_port(self.api_port)}"
        else:
            return f"https://{self.container_alias}:{self.api_port}"

    def get_imds_endpoint(self, network_type: NetworkType = NetworkType.LOCAL) -> str:
        if network_type == NetworkType.LOCAL:
            return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self.metadata_port)}"
        else:
            return f"http://{self.container_alias}:{self.metadata_port}"

    def get_token_url(self, network_type: NetworkType = NetworkType.LOCAL) -> str:
        base_url = self.get_imds_endpoint(network_type=network_type)
        return f"{base_url}/metadata/identity/oauth2/token"

    def get_token(self, network_type: NetworkType = NetworkType.LOCAL) -> StaticTokenCredential:
        resource = self.get_connection_url(network_type=network_type)
        token_url = self.get_token_url(network_type=network_type)
        json_response = requests.get(f"{token_url}?resource={resource}").json()
        return StaticTokenCredential(json_token=json_response)
