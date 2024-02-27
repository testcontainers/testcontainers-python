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
import socket
from typing import Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready


class AzuriteContainer(DockerContainer):
    """
    The example below spins up an Azurite container and
    shows an example to create a Blob service client with the container. The method
    :code:`get_connection_string` can be used to create a client for Blob service, Queue service
    and Table service.

    Example:

        .. doctest::

            >>> from testcontainers.azurite import AzuriteContainer
            >>> from azure.storage.blob import BlobServiceClient

            >>> with AzuriteContainer() as azurite_container:
            ...   connection_string = azurite_container.get_connection_string()
            ...   client = BlobServiceClient.from_connection_string(
            ...        connection_string,
            ...        api_version="2019-12-12"
            ...   )
    """

    def __init__(
        self,
        image: str = "mcr.microsoft.com/azure-storage/azurite:latest",
        *,
        blob_service_port: int = 10_000,
        queue_service_port: int = 10_001,
        table_service_port: int = 10_002,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Constructs an AzuriteContainer.

        Args:
            image: Expects an image with tag.
            **kwargs: Keyword arguments passed to super class.
        """
        super().__init__(image=image, **kwargs)
        self.account_name = account_name or os.environ.get("AZURITE_ACCOUNT_NAME", "devstoreaccount1")
        self.account_key = account_key or os.environ.get(
            "AZURITE_ACCOUNT_KEY",
            "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/" "K1SZFPTOtr/KBHBeksoGMGw==",
        )

        raise_for_deprecated_parameter(kwargs, "ports_to_expose", "container.with_exposed_ports")
        self.blob_service_port = blob_service_port
        self.queue_service_port = queue_service_port
        self.table_service_port = table_service_port

        self.with_exposed_ports(blob_service_port, queue_service_port, table_service_port)
        self.with_env("AZURITE_ACCOUNTS", f"{self.account_name}:{self.account_key}")

    def get_connection_string(self) -> str:
        host_ip = self.get_container_host_ip()
        connection_string = (
            f"DefaultEndpointsProtocol=http;" f"AccountName={self.account_name};" f"AccountKey={self.account_key};"
        )

        if self.blob_service_port in self.ports:
            connection_string += (
                f"BlobEndpoint=http://{host_ip}:"
                f"{self.get_exposed_port(self.blob_service_port)}"
                f"/{self.account_name};"
            )

        if self.queue_service_port in self.ports:
            connection_string += (
                f"QueueEndpoint=http://{host_ip}:"
                f"{self.get_exposed_port(self.queue_service_port)}"
                f"/{self.account_name};"
            )

        if self.table_service_port in self.ports:
            connection_string += (
                f"TableEndpoint=http://{host_ip}:"
                f"{self.get_exposed_port(self.table_service_port)}"
                f"/{self.account_name};"
            )

        return connection_string

    def start(self) -> "AzuriteContainer":
        super().start()
        self._connect()
        return self

    @wait_container_is_ready(OSError)
    def _connect(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.get_container_host_ip(), int(self.get_exposed_port(next(iter(self.ports))))))
