import os
from enum import Enum
from typing import Any, NamedTuple, Optional

import requests

from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

# This comment can be removed (Used for testing)


class StaticToken(NamedTuple):
    """Represents an OAuth access token."""

    token: str
    """The token string."""
    expires_on: int
    """The token's expiration time in Unix time."""


class StaticTokenCredential:
    def __init__(self, json_token: str):
        self.access_token = StaticToken(token=json_token.get("access_token"), expires_on=json_token.get("expires_on"))

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> StaticToken:
        return self.access_token


class NetworkType(Enum):
    NETWORK = "network"
    LOCAL = "local"


class LowkeyVaultContainer(DockerContainer):
    """
    Container for a Lowkey Vault instance for emulating Azure Key Vault.
    Supports Key, Secret and Certificate APIs.

    Example:

        .. doctest::

            >>> from azure.core.pipeline.transport._requests_basic import RequestsTransport
            >>> from azure.keyvault.secrets import SecretClient
            >>> from testcontainers.lowkeyvault import LowkeyVaultContainer

            >>> with LowkeyVaultContainer() as lowkey_vault:
            ...    connection_url = lowkey_vault.get_connection_url()
            ...    token = lowkey_vault.get_token()
            ...    # don't fail due to the self-signed certificate
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
        self, image: str = "nagyesta/lowkey-vault:7.0.9-ubi10-minimal", container_alias: Optional[str] = None, **kwargs
    ) -> None:
        super().__init__(image, **kwargs)
        self.api_port = 8443
        self.metadata_port = 8080
        self.with_exposed_ports(self.api_port, self.metadata_port)
        self.with_env("LOWKEY_VAULT_RELAXED_PORTS", "true")
        container_host_ip: str = self.get_container_host_ip()
        if container_alias is not None:
            self.with_network_aliases(container_alias)
            self.container_alias = container_alias
            self.with_env("LOWKEY_VAULT_ALIASES", f"localhost={container_alias}:<port>")
        elif container_host_ip != "localhost":
            self.with_env("LOWKEY_VAULT_ALIASES", f"localhost={container_host_ip}:<port>")
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

    def auto_set_local_managed_identity_env_variables(self):
        imds_endpoint: str = self.get_imds_endpoint(network_type=NetworkType.LOCAL)
        token_url: str = self.get_token_url(network_type=NetworkType.LOCAL)
        os.environ["AZURE_POD_IDENTITY_AUTHORITY_HOST"] = imds_endpoint
        os.environ["IMDS_ENDPOINT"] = imds_endpoint
        os.environ["IDENTITY_ENDPOINT"] = token_url

    def get_token_url(self, network_type: NetworkType = NetworkType.LOCAL) -> str:
        base_url = self.get_imds_endpoint(network_type=network_type)
        return f"{base_url}/metadata/identity/oauth2/token"

    def get_token(self, network_type: NetworkType = NetworkType.LOCAL) -> StaticTokenCredential:
        resource = self.get_connection_url(network_type=network_type)
        token_url = self.get_token_url(network_type=network_type)
        json_response = requests.get(f"{token_url}?resource={resource}").json()
        return StaticTokenCredential(json_token=json_response)
