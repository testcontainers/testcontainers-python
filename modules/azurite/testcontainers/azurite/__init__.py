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
import enum
import os
import socket
from typing import Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready


class ConnectionStringType(enum.Enum):
    """
    Enumeration for specifying the type of connection string to generate for Azurite.

    :cvar LOCALHOST: Represents a connection string for access from the host machine
                     where the tests are running.
    :cvar NETWORK: Represents a connection string for access from another container
                   within the same Docker network as the Azurite container.
    """

    LOCALHOST = "localhost"
    NETWORK = "network"


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
            "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
        )

        raise_for_deprecated_parameter(kwargs, "ports_to_expose", "container.with_exposed_ports")
        self.blob_service_port = blob_service_port
        self.queue_service_port = queue_service_port
        self.table_service_port = table_service_port

        self.with_exposed_ports(blob_service_port, queue_service_port, table_service_port)
        self.with_env("AZURITE_ACCOUNTS", f"{self.account_name}:{self.account_key}")

    def get_connection_string(
        self, connection_string_type: ConnectionStringType = ConnectionStringType.LOCALHOST
    ) -> str:
        """Retrieves the appropriate connection string for the Azurite container based on the specified access type.

        This method acts as a dispatcher, returning a connection string optimized
        either for access from the host machine or for inter-container communication within the same Docker network.

        :param connection_string_type: The type of connection string to generate.
                Use :attr:`ConnectionStringType.LOCALHOST` for connections
                    from the machine running the tests (default), or
                :attr:`ConnectionStringType.NETWORK` for connections
                    from other containers within the same Docker network.
        :type connection_string_type: ConnectionStringType
        :return: The generated Azurite connection string.
        :rtype: str
        :raises ValueError: If an unrecognized `connection_string_type` is provided.
        """
        if connection_string_type == ConnectionStringType.LOCALHOST:
            return self.__get_local_connection_string()
        elif connection_string_type == ConnectionStringType.NETWORK:
            return self.__get_external_connection_string()
        else:
            raise ValueError(
                f"unrecognized connection string type {connection_string_type}, "
                f"Supported values are ConnectionStringType.LOCALHOST or ConnectionStringType.NETWORK "
            )

    def __get_local_connection_string(self) -> str:
        """Generates a connection string for Azurite accessible from the local host machine.

        This connection string uses the Docker host IP address (obtained via
        :meth:`testcontainers.core.container.DockerContainer.get_container_host_ip`)
        and the dynamically exposed ports of the Azurite container. This ensures that
        clients running on the host can connect successfully to the Azurite services.

        :return: The Azurite connection string for local host access.
        :rtype: str
        """
        host_ip = self.get_container_host_ip()
        connection_string = (
            f"DefaultEndpointsProtocol=http;AccountName={self.account_name};AccountKey={self.account_key};"
        )

        if self.blob_service_port in self.ports:
            connection_string += (
                f"BlobEndpoint=http://{host_ip}:{self.get_exposed_port(self.blob_service_port)}/{self.account_name};"
            )

        if self.queue_service_port in self.ports:
            connection_string += (
                f"QueueEndpoint=http://{host_ip}:{self.get_exposed_port(self.queue_service_port)}/{self.account_name};"
            )

        if self.table_service_port in self.ports:
            connection_string += (
                f"TableEndpoint=http://{host_ip}:{self.get_exposed_port(self.table_service_port)}/{self.account_name};"
            )

        return connection_string

    def __get_external_connection_string(self) -> str:
        """Generates a connection string for Azurite, primarily optimized for
        inter-container communication within a custom Docker network.

        This method attempts to provide the most suitable connection string
        based on the container's network configuration:

        - **For Inter-Container Communication (Recommended):** If the Azurite container is
          part of a custom Docker network and has network aliases configured,
          the connection string will use the first network alias as the hostname
          and the internal container ports (e.g., #$#`http://<alias>:<internal_port>/<account_name>`#$#).
          This is the most efficient and robust way for other containers
          in the same network to connect to Azurite, leveraging Docker's internal DNS.

        - **Fallback for Non-Networked/Aliased Scenarios:** If the container is
          not on a custom network with aliases (e.g., running on the default
          bridge network without explicit aliases), the method falls back to
          using the Docker host IP (obtained via
          :meth:`testcontainers.core.container.DockerContainer.get_container_host_ip`)
          and the dynamically exposed ports (e.g., #$#`http://<host_ip>:<exposed_port>/<account_name>`#$#).
          While this connection string is technically "external" to the container,
          it primarily facilitates connections *from the host machine*.

        :return: The generated Azurite connection string.
        :rtype: str
        """
        # Check if we're on a custom network and have network aliases
        if hasattr(self, "_network") and self._network and hasattr(self, "_network_aliases") and self._network_aliases:
            # Use the first network alias for inter-container communication
            host_ip = self._network_aliases[0]
            # When using network aliases, use the internal container ports
            blob_port = self.blob_service_port
            queue_port = self.queue_service_port
            table_port = self.table_service_port
        else:
            # Use the Docker host IP for external connections
            host_ip = self.get_container_host_ip()
            # When using host IP, use the exposed ports
            blob_port = (
                self.get_exposed_port(self.blob_service_port)
                if self.blob_service_port in self.ports
                else self.blob_service_port
            )
            queue_port = (
                self.get_exposed_port(self.queue_service_port)
                if self.queue_service_port in self.ports
                else self.queue_service_port
            )
            table_port = (
                self.get_exposed_port(self.table_service_port)
                if self.table_service_port in self.ports
                else self.table_service_port
            )

        connection_string = (
            f"DefaultEndpointsProtocol=http;AccountName={self.account_name};AccountKey={self.account_key};"
        )

        if self.blob_service_port in self.ports:
            connection_string += f"BlobEndpoint=http://{host_ip}:{blob_port}/{self.account_name};"

        if self.queue_service_port in self.ports:
            connection_string += f"QueueEndpoint=http://{host_ip}:{queue_port}/{self.account_name};"

        if self.table_service_port in self.ports:
            connection_string += f"TableEndpoint=http://{host_ip}:{table_port}/{self.account_name};"

        return connection_string

    def start(self) -> "AzuriteContainer":
        super().start()
        self._connect()
        return self

    @wait_container_is_ready(OSError)
    def _connect(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.get_container_host_ip(), int(self.get_exposed_port(next(iter(self.ports))))))
