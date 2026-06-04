from azure.core.exceptions import ServiceRequestError
from azure.cosmos import CosmosClient as SyncCosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

from testcontainers.core.waiting_utils import wait_container_is_ready

from ._emulator import CosmosDBEmulatorContainer

__all__ = ["CosmosDBNoSQLEndpointContainer"]

NOSQL_PORT = 8081


class CosmosDBNoSQLEndpointContainer(CosmosDBEmulatorContainer):
    """
    CosmosDB NoSQL enpoint Emulator.

    Example:

        .. code-block:: python

            >>> from testcontainers.cosmosdb import CosmosDBNoSQLEndpointContainer
            >>> with CosmosDBNoSQLEndpointContainer() as emulator:
            ...   db = emulator.insecure_sync_client().create_database_if_not_exists("test")

        .. code-block:: python

            >>> from testcontainers.cosmosdb import CosmosDBNoSQLEndpointContainer
            >>> from azure.cosmos import CosmosClient

            >>> with CosmosDBNoSQLEndpointContainer() as emulator:
            ...   client = CosmosClient(url=emulator.url, credential=emulator.key, connection_verify=False)
            ...   db = client.create_database_if_not_exists("test")

    """

    def __init__(self, **kwargs):
        super().__init__(endpoint_ports=[NOSQL_PORT], **kwargs)

    @property
    def port(self) -> str:
        """
        The exposed port to the NoSQL endpoint
        """
        return self.get_exposed_port(NOSQL_PORT)

    @property
    def url(self) -> str:
        """
        The url to the NoSQL endpoint
        """
        return f"https://{self.host}:{self.port}"

    def insecure_async_client(self):
        """
        Returns an asynchronous CosmosClient instance
        """
        return AsyncCosmosClient(url=self.url, credential=self.key, connection_verify=False)

    def insecure_sync_client(self):
        """
        Returns a synchronous CosmosClient instance
        """
        return SyncCosmosClient(url=self.url, credential=self.key, connection_verify=False)

    @wait_container_is_ready(ServiceRequestError)
    def _wait_for_query_success(self) -> None:
        with self.insecure_sync_client() as c:
            list(c.list_databases())
