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
from typing import TYPE_CHECKING, Optional

from requests import ConnectionError, get

from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_container_is_ready

if TYPE_CHECKING:
    from requests import Response


class WeaviateContainer(DbContainer):
    """
    Weaviate vector database container.

    Arguments:
        `image`
            Docker image to use with Weaviate container.
        `env_vars`
            Additional environment variables to include with the container, e.g. ENABLE_MODULES list, QUERY_DEFAULTS_LIMIT setting.

    Example:
        This example shows how to start Weaviate container with default settings.

        .. doctest::

            >>> from testcontainers.weaviate import WeaviateContainer

            >>> with WeaviateContainer() as container:
            ...     with container.get_client() as client:
            ...         client.is_live()
            True

        This example shows how to start Weaviate container with additional settings.

        .. doctest::

            >>> from testcontainers.weaviate import WeaviateContainer

            >>> with WeaviateContainer(
            ...     env_vars={
            ...         "ENABLE_MODULES": "backup-filesystem,text2vec-openai",
            ...         "BACKUP_FILESYSTEM_PATH": "/tmp/backups",
            ...         "QUERY_DEFAULTS_LIMIT": 100,
            ...     }
            ... ) as container:
            ...     with container.get_client() as client:
            ...         client.is_live()
            True
    """

    def __init__(
        self,
        image: str = "semitechnologies/weaviate:1.24.5",
        env_vars: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)
        self._http_port = 8080
        self._grpc_port = 50051

        self.with_command(f"--host 0.0.0.0 --scheme http --port {self._http_port}")
        self.with_exposed_ports(self._http_port, self._grpc_port)

        if env_vars is not None:
            for key, value in env_vars.items():
                self.with_env(key, value)

    def _configure(self) -> None:
        self.with_env("AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED", "true")
        self.with_env("PERSISTENCE_DATA_PATH", "/var/lib/weaviate")

    @wait_container_is_ready(ConnectionError)
    def _connect(self) -> None:
        url = f"http://{self.get_http_host()}:{self.get_http_port()}/v1/.well-known/ready"
        response: Response = get(url)
        response.raise_for_status()

    def get_client(
        self,
        headers: Optional[dict[str, str]] = None,
    ):
        """
        Get a `weaviate.WeaviateClient` instance associated with the container.

        Arguments:
            `headers`
                Additional headers to include in the requests, e.g. API keys for third-party Cloud vectorization.

        Returns:
            WeaviateClient: An instance of the `weaviate.WeaviateClient` class.
        """

        try:
            import weaviate
        except ImportError as e:
            raise ImportError("To use the `get_client` method, you must install the `weaviate-client` package.") from e
        return weaviate.connect_to_custom(
            http_host=self.get_http_host(),
            http_port=self.get_http_port(),
            http_secure=self.get_http_secure(),
            grpc_host=self.get_http_host(),
            grpc_port=self.get_grpc_port(),
            grpc_secure=self.get_grpc_secure(),
            headers=headers,
        )

    def get_http_host(self) -> str:
        """
        Get the HTTP host of Weaviate container.

        Returns:
            `str`
                The HTTP host of Weaviate container.
        """
        return f"{self.get_container_host_ip()}"

    def get_http_port(self) -> int:
        """
        Get the HTTP port of Weaviate container.

        Returns:
            `int`
                The HTTP port of Weaviate container.
        """
        return self.get_exposed_port(self._http_port)

    def get_http_secure(self) -> bool:
        """
        Get the HTTP secured setting of Weaviate container.

        Returns:
            `bool`
                True if it's https.
        """
        return False

    def get_grpc_host(self) -> str:
        """
        Get the gRPC host of Weaviate container.

        Returns:
            `str`
                The gRPC host of Weaviate container.
        """
        return f"{self.get_container_host_ip()}"

    def get_grpc_port(self) -> int:
        """
        Get the gRPC port of Weaviate container.

        Returns:
            `int`
                The gRPC port of Weaviate container.
        """
        return self.get_exposed_port(self._grpc_port)

    def get_grpc_secure(self) -> bool:
        """
        Get the gRPC secured setting of Weaviate container.

        Returns:
            `str`
                True if the conntection is secured with SSL.
        """
        return False
