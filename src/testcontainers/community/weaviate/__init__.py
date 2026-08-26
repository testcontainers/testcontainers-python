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
import contextlib
from typing import Optional

from docker.types import IPAMConfig, IPAMPool
from typing_extensions import Self

from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import HttpWaitStrategy


class WeaviateContainer(DockerContainer):
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

            >>> from testcontainers.community.weaviate import WeaviateContainer

            >>> with WeaviateContainer() as container:
            ...     with container.get_client() as client:
            ...         client.is_live()
            True

        This example shows how to start Weaviate container with additional settings.

        .. doctest::

            >>> from testcontainers.community.weaviate import WeaviateContainer

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
        image: str = "semitechnologies/weaviate:1.28.4",
        env_vars: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)
        self._http_port = 8080
        self._grpc_port = 50051

        # Weaviate's memberlist gossip requires an RFC1918 private IP to advertise.
        # Docker bridge subnets are not always in RFC1918 ranges, so we create a
        # dedicated network using 10.10.10.0/24 which is always recognised as private.
        self._weaviate_network = Network(
            docker_network_kw={"ipam": IPAMConfig(pool_configs=[IPAMPool(subnet="10.10.10.0/24")])}
        )
        self.with_network(self._weaviate_network)
        self.with_exposed_ports(self._http_port, self._grpc_port)
        self.waiting_for(HttpWaitStrategy(self._http_port, "/v1/.well-known/ready"))

        if env_vars is not None:
            for key, value in env_vars.items():
                self.with_env(key, value)

    def _configure(self) -> None:
        self.with_env("HOST", "0.0.0.0")
        self.with_env("PORT", str(self._http_port))
        self.with_env("SCHEME", "http")
        self.with_env("AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED", "true")
        self.with_env("PERSISTENCE_DATA_PATH", "/var/lib/weaviate")
        self.with_env("DEFAULT_VECTORIZER_MODULE", "none")
        self.with_env("CLUSTER_HOSTNAME", "node1")

    def start(self) -> Self:
        self._weaviate_network.create()
        return super().start()

    def stop(self, force: bool = True, delete_volume: bool = True) -> None:
        super().stop(force=force, delete_volume=delete_volume)
        if self._weaviate_network._network is not None:
            with contextlib.suppress(Exception):
                self._weaviate_network.remove()

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
