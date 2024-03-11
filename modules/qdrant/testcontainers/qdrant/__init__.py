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
from functools import cached_property
from pathlib import Path
from typing import Optional

from qdrant_client import AsyncQdrantClient, QdrantClient

from testcontainers.core.config import TIMEOUT
from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class QdrantContainer(DbContainer):
    """
    Qdrant vector database container.

    Example:
        .. doctest::

            >>> from testcontainers.qdrant import QdrantContainer

            >>> with QdrantContainer(api_key="<OPTIONAL_API_KEY>") as qdrant:
            ...     client = qdrant.get_client()
            ...     client.get_collections()
    """

    QDRANT_CONFIG_FILE_PATH = "/qdrant/config/config.yaml"

    def __init__(
        self,
        image: str = "qdrant/qdrant:latest",
        rest_port: int = 6333,
        grpc_port: int = 6334,
        api_key: Optional[str] = None,
        config_file_path: Optional[Path] = None,
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)
        self.rest_port = rest_port
        self.grpc_port = grpc_port
        self.api_key = api_key or os.getenv("QDRANT_CONTAINER_API_KEY")

        if config_file_path:
            self.with_volume_mapping(host=str(config_file_path), container=QdrantContainer.QDRANT_CONFIG_FILE_PATH)

        self.with_exposed_ports(self.rest_port, self.grpc_port)

    def _configure(self) -> None:
        self.with_env("QDRANT__SERVICE__API_KEY", self.api_key)

    @wait_container_is_ready()
    def _connect(self) -> None:
        wait_for_logs(self, ".*Actix runtime found; starting in Actix runtime.*", TIMEOUT)

    def get_client(self, **kwargs) -> "QdrantClient":
        """
        Get a `qdrant_client.QdrantClient` instance associated with the container.

        Args:
            **kwargs: Additional keyword arguments to be passed to the `qdrant_client.QdrantClient` constructor.

        Returns:
            QdrantClient: An instance of the `qdrant_client.QdrantClient` class.

        """
        return QdrantClient(
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.rest_port),
            grpc_port=self.get_exposed_port(self.grpc_port),
            api_key=self.api_key,
            https=False,
            **kwargs,
        )

    def get_async_client(self, **kwargs) -> "AsyncQdrantClient":
        """
        Get a `qdrant_client.AsyncQdrantClient` instance associated with the container.

        Args:
            **kwargs: Additional keyword arguments to be passed to the `qdrant_client.AsyncQdrantClient` constructor.

        Returns:
            QdrantClient: An instance of the `qdrant_client.AsyncQdrantClient` class.

        """
        return AsyncQdrantClient(
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.rest_port),
            grpc_port=self.get_exposed_port(self.grpc_port),
            api_key=self.api_key,
            https=False,
            **kwargs,
        )

    @cached_property
    def rest_host_address(self) -> str:
        """
        Get the REST host address of the Qdrant container.

        Returns:
            str: The REST host address of the Qdrant container.
        """
        return f"{self.get_container_host_ip()}:{self.get_exposed_port(self.rest_port)}"

    @cached_property
    def grpc_host_address(self) -> str:
        """
        Get the GRPC host address of the Qdrant container.

        Returns:
            str: The GRPC host address of the Qdrant container.
        """
        return f"{self.get_container_host_ip()}:{self.get_exposed_port(self.grpc_port)}"
