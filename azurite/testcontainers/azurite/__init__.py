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

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class AzuriteContainer(DockerContainer):
    """
        The example below spins up an Azurite container and
        shows an example to create a Blob service client with the container. The method
        :code:`get_connection_string` can be used to create a client for Blob service, Queue service
        and Table service.

        Example
        -------
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

    _AZURITE_ACCOUNT_NAME = os.environ.get("AZURITE_ACCOUNT_NAME", "devstoreaccount1")
    _AZURITE_ACCOUNT_KEY = os.environ.get("AZURITE_ACCOUNT_KEY", "Eby8vdM02xNOcqFlqUwJPLlmEtlCDX"
                                          "J1OUzFT50uSRZ6IFsuFq2UVErCz4I6"
                                          "tq/K1SZFPTOtr/KBHBeksoGMGw==")

    _BLOB_SERVICE_PORT = 10_000
    _QUEUE_SERVICE_PORT = 10_001
    _TABLE_SERVICE_PORT = 10_002

    def __init__(
            self,
            image="mcr.microsoft.com/azure-storage/azurite:latest",
            ports_to_expose=None,
            **kwargs
    ):
        """ Constructs an AzuriteContainer.

        Parameters
        ----------
        image: str
            Expects an image with tag.
        ports_to_expose: List[int]
            Expects a list with port numbers to expose.
        kwargs
        """
        super().__init__(image=image, **kwargs)

        if ports_to_expose is None:
            ports_to_expose = [
                self._BLOB_SERVICE_PORT,
                self._QUEUE_SERVICE_PORT,
                self._TABLE_SERVICE_PORT
            ]

        if len(ports_to_expose) == 0:
            raise ValueError("Expected a list with port numbers to expose")

        self.with_exposed_ports(*ports_to_expose)
        self.with_env("AZURITE_ACCOUNTS",
                      f"{self._AZURITE_ACCOUNT_NAME}:{self._AZURITE_ACCOUNT_KEY}")

    def get_connection_string(self):
        host_ip = self.get_container_host_ip()
        connection_string = f"DefaultEndpointsProtocol=http;" \
                            f"AccountName={self._AZURITE_ACCOUNT_NAME};" \
                            f"AccountKey={self._AZURITE_ACCOUNT_KEY};"

        if self._BLOB_SERVICE_PORT in self.ports:
            connection_string += f"BlobEndpoint=http://{host_ip}:" \
                                 f"{self.get_exposed_port(self._BLOB_SERVICE_PORT)}" \
                                 f"/{self._AZURITE_ACCOUNT_NAME};"

        if self._QUEUE_SERVICE_PORT in self.ports:
            connection_string += f"QueueEndpoint=http://{host_ip}:" \
                                 f"{self.get_exposed_port(self._QUEUE_SERVICE_PORT)}" \
                                 f"/{self._AZURITE_ACCOUNT_NAME};"

        if self._TABLE_SERVICE_PORT in self.ports:
            connection_string += f"TableEndpoint=http://{host_ip}:" \
                                 f"{self.get_exposed_port(self._TABLE_SERVICE_PORT)}" \
                                 f"/{self._AZURITE_ACCOUNT_NAME};"

        return connection_string

    def start(self):
        super().start()
        self._connect()
        return self

    @wait_container_is_ready(OSError)
    def _connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.get_container_host_ip(),
                       int(self.get_exposed_port(next(iter(self.ports))))))
