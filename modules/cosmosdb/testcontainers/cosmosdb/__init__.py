import os
import socket
import ssl
from collections.abc import Iterable
from enum import Enum, auto
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from azure.core.exceptions import ServiceRequestError
from azure.cosmos import CosmosClient as SyncCosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from typing_extensions import Self

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs

__all__ = ["CosmosDBEmulatorContainer", "Endpoints"]


class Endpoints(Enum):
    Direct = auto()
    Gremlin = auto()
    Table = auto()
    MongoDB = auto()
    Cassandra = auto()


ALL_ENDPOINTS = set(Endpoints)

# Ports mostly derived from https://docs.microsoft.com/en-us/azure/cosmos-db/emulator-command-line-parameters
EMULATOR_PORT = 8081
endpoint_ports = {
    Endpoints.Direct: frozenset([10251, 10252, 10253, 10254]),
    Endpoints.Gremlin: frozenset([8901]),
    Endpoints.Table: frozenset([8902]),
    Endpoints.MongoDB: frozenset([10255]),
    Endpoints.Cassandra: frozenset([10350]),
}


def is_truthy_string(s: str):
    return s.lower().strip() in {"true", "yes", "y", "1"}


class CosmosDBEmulatorContainer(DockerContainer):
    """
    CosmosDB Emulator container.

    Example:
        .. doctest::
                >>> from testcontainers.cosmosdb import CosmosDBEmulatorContainer
                >>> with CosmosDBEmulatorContainer() as cosmosdb:
                ...    db = cosmosdb.sync_client().create_database_if_not_exists("test")

        .. doctest::
                >>> from testcontainers.cosmosdb import CosmosDBEmulatorContainer
                >>> with CosmosDBEmulatorContainer() as emulator:
                ...    cosmosdb = CosmosClient(url=emulator.url, credential=emulator.key, connection_verify=False)
                ...    db = cosmosdb.create_database_if_not_exists("test")

        .. doctest::
                >>> from testcontainers.cosmosdb import CosmosDBEmulatorContainer, Endpoints
                >>> with CosmosDBEmulatorContainer(endpoints=[Endpoints.MongoDB]) as emulator:
                ...    print(f"Point yout MongoDB client to {emulator.host}:{emulator.ports(Endpoints.MongoDB)[0]}")
    """

    def __init__(
        self,
        image: str = os.getenv(
            "AZURE_COSMOS_EMULATOR_IMAGE", "mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest"
        ),
        partition_count: int = os.getenv("AZURE_COSMOS_EMULATOR_PARTITION_COUNT", None),
        enable_data_persistence: bool = is_truthy_string(
            os.getenv("AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE", "false")
        ),
        bind_ports: bool = is_truthy_string(os.getenv("AZURE_COSMOS_EMULATOR_BIND_PORTS", "true")),
        key: str = os.getenv(
            "AZURE_COSMOS_EMULATOR_KEY",
            "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
        ),
        endpoints: Iterable[Endpoints] = [],  # the emulator image does not support host-container port mapping
        **docker_client_kw,
    ):
        super().__init__(image=image, **docker_client_kw)
        self.partition_count = partition_count
        self.key = key
        self.enable_data_persistence = enable_data_persistence
        self.endpoints = frozenset(endpoints)
        self.bind_ports = bind_ports

    def start(self) -> Self:
        self._configure()
        super().start()
        self._wait_until_ready()
        return self

    @property
    def url(self) -> str:
        """
        Returns the url to interact with the emulator
        """
        return f"https://{self.host}:{self.get_exposed_port(EMULATOR_PORT)}"

    @property
    def host(self) -> str:
        return self.get_container_host_ip()

    def ports(self, endpoint: Endpoints) -> Iterable[int]:
        assert endpoint in self.endpoints, f"Endpoint {endpoint} is not exposed"
        return {self.get_exposed_port(p) for p in endpoint_ports[endpoint]}

    def async_client(self) -> AsyncCosmosClient:
        """
        Returns an asynchronous CosmosClient instance to interact with the CosmosDB server
        """
        return AsyncCosmosClient(url=self.url, credential=self.key, connection_verify=False)

    def sync_client(self) -> SyncCosmosClient:
        """
        Returns a synchronous CosmosClient instance to interact with the CosmosDB server
        """
        return SyncCosmosClient(url=self.url, credential=self.key, connection_verify=False)

    def _configure(self) -> None:
        self.with_bind_ports(EMULATOR_PORT, EMULATOR_PORT)

        endpoints_ports = []
        for endpoint in self.endpoints:
            endpoints_ports.extend(endpoint_ports[endpoint])

        if self.bind_ports:
            [self.with_bind_ports(port, port) for port in endpoints_ports]
        else:
            self.with_exposed_ports(*endpoints_ports)

        (
            self.with_env("AZURE_COSMOS_EMULATOR_PARTITION_COUNT", str(self.partition_count))
            .with_env("AZURE_COSMOS_EMULATOR_IP_ADDRESS_OVERRIDE", socket.gethostbyname(socket.gethostname()))
            .with_env("AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE", str(self.enable_data_persistence))
            .with_env("AZURE_COSMOS_EMULATOR_KEY", str(self.key))
        )

    def _wait_until_ready(self) -> Self:
        """
        Waits until the CosmosDB Emulator image is ready to be used.
        """
        (
            self._wait_for_logs(container=self, predicate="Started\\s*$")
            ._wait_for_url(f"{self.url}/_explorer/index.html")
            ._wait_for_query_success(lambda sync_client: list(sync_client.list_databases()))
        )
        return self

    @wait_container_is_ready(HTTPError, URLError)
    def _wait_for_url(self, url: str) -> Self:
        with urlopen(url, context=ssl._create_unverified_context()) as response:
            response.read()
        return self

    def _wait_for_logs(self, *args, **kwargs) -> Self:
        wait_for_logs(*args, **kwargs)
        return self

    @wait_container_is_ready(ServiceRequestError)
    def _wait_for_query_success(self, query: Callable[[SyncCosmosClient], None]) -> Self:
        with self.sync_client() as c:
            query(c)
        return self
