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

from qdrant_client import QdrantClient

from testcontainers.core.config import TIMEOUT
from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class QdrantContainer(DbContainer):
    QDRANT_CONFIG_FILE_PATH = "/qdrant/config/config.yaml"

    def __init__(
        self,
        image: str = "qdrant/qdrant:latest",
        rest_port: int = 6333,
        grpc_port: int = 6334,
        container_api_key: Optional[str] = None,
        config_file_path: Optional[Path] = None,
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)
        self.rest_port = rest_port
        self.grpc_port = grpc_port
        self.container_api_key = container_api_key or os.getenv("QDRANT_CONTAINER_API_KEY")

        if config_file_path:
            self.with_volume_mapping(host=str(config_file_path), container=QdrantContainer.QDRANT_CONFIG_FILE_PATH)

        self.with_exposed_ports(self.rest_port, self.grpc_port)

    def _configure(self) -> None:
        self.with_env("QDRANT__SERVICE__API_KEY", self.container_api_key)

    @wait_container_is_ready()
    def _connect(self) -> None:
        wait_for_logs(self, ".*Actix runtime found; starting in Actix runtime.*", TIMEOUT)

    def get_client(self, **kwargs) -> "QdrantClient":
        return QdrantClient(
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.rest_port),
            grpc_port=self.get_exposed_port(self.grpc_port),
            api_key=self.container_api_key,
            **kwargs,
        )

    @cached_property
    def http_host_address(self) -> str:
        return f"{self.get_container_host_ip()}:{self.get_exposed_port(self.rest_port)}"

    @cached_property
    def grpc_host_address(self) -> str:
        return f"{self.get_container_host_ip()}:{self.get_exposed_port(self.grpc_port)}"
