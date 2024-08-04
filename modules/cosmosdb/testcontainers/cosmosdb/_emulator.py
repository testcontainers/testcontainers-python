import os
import socket
import ssl
from collections.abc import Iterable
from distutils.util import strtobool
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from typing_extensions import Self

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs

from . import _grab as grab

__all__ = ["CosmosDBEmulatorContainer"]

EMULATOR_PORT = 8081


class CosmosDBEmulatorContainer(DockerContainer):
    """
    Abstract class for CosmosDB Emulator endpoints.

    Concrete implementations for each endpoint is provided by a separate class:
    NoSQLEmulatorContainer and MongoDBEmulatorContainer.
    """

    def __init__(
        self,
        image: str = os.getenv(
            "AZURE_COSMOS_EMULATOR_IMAGE", "mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest"
        ),
        partition_count: int = os.getenv("AZURE_COSMOS_EMULATOR_PARTITION_COUNT", None),
        enable_data_persistence: bool = strtobool(os.getenv("AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE", "false")),
        key: str = os.getenv(
            "AZURE_COSMOS_EMULATOR_KEY",
            "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
        ),
        bind_ports: bool = strtobool(os.getenv("AZURE_COSMOS_EMULATOR_BIND_PORTS", "true")),
        endpoint_ports: Iterable[int] = [],
        **other_kwargs,
    ):
        super().__init__(image=image, **other_kwargs)
        self.endpoint_ports = endpoint_ports
        self.partition_count = partition_count
        self.key = key
        self.enable_data_persistence = enable_data_persistence
        self.bind_ports = bind_ports

    @property
    def host(self) -> str:
        """
        Emulator host
        """
        return self.get_container_host_ip()

    @property
    def server_certificate_pem(self) -> bytes:
        """
        PEM-encoded server certificate
        """
        return self._cert_pem_bytes

    def start(self) -> Self:
        self._configure()
        super().start()
        self._wait_until_ready()
        self._cert_pem_bytes = self._download_cert()
        return self

    def _configure(self) -> None:
        all_ports = {EMULATOR_PORT, *self.endpoint_ports}
        if self.bind_ports:
            for port in all_ports:
                self.with_bind_ports(port, port)
        else:
            self.with_exposed_ports(*all_ports)

        (
            self.with_env("AZURE_COSMOS_EMULATOR_PARTITION_COUNT", str(self.partition_count))
            .with_env("AZURE_COSMOS_EMULATOR_IP_ADDRESS_OVERRIDE", socket.gethostbyname(socket.gethostname()))
            .with_env("AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE", str(self.enable_data_persistence))
            .with_env("AZURE_COSMOS_EMULATOR_KEY", str(self.key))
        )

    def _wait_until_ready(self) -> Self:
        wait_for_logs(container=self, predicate="Started\\s*$")

        if self.bind_ports:
            self._wait_for_url(f"https://{self.host}:{EMULATOR_PORT}/_explorer/index.html")
            self._wait_for_query_success()

        return self

    def _download_cert(self) -> bytes:
        with grab.file(
            self.get_wrapped_container(),
            "/tmp/cosmos/appdata/.system/profiles/Client/AppData/Local/CosmosDBEmulator/emulator.pem",
        ) as cert:
            return cert.read()

    @wait_container_is_ready(HTTPError, URLError)
    def _wait_for_url(self, url: str) -> Self:
        with urlopen(url, context=ssl._create_unverified_context()) as response:
            response.read()
        return self

    def _wait_for_query_success(self) -> None:
        pass
