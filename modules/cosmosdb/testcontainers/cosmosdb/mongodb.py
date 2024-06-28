import os

from ._emulator import CosmosDBEmulatorContainer

__all__ = ["CosmosDBMongoEndpointContainer"]

ENDPOINT_PORT = 10255


class CosmosDBMongoEndpointContainer(CosmosDBEmulatorContainer):
    """
    CosmosDB MongoDB enpoint Emulator.

    Example:

        .. code-block:: python

            >>> from testcontainers.cosmosdb import CosmosDBMongoEndpointContainer

            >>> with CosmosDBMongoEndpointContainer(mongodb_version="4.0") as emulator:
            ...   print(f"Point your MongoDB client at {emulator.host}:{emulator.port} using key {emulator.key}")
            ...   print(f"and eiher disable TLS server auth or trust the server's self signed cert (emulator.server_certificate_pem)")

    """

    def __init__(
        self,
        mongodb_version: str,
        image: str = os.getenv(
            "AZURE_COSMOS_EMULATOR_IMAGE", "mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:mongodb"
        ),
        **other_kwargs,
    ):
        super().__init__(image=image, endpoint_ports=[ENDPOINT_PORT], **other_kwargs)
        assert mongodb_version is not None, "A MongoDB version is required to use the MongoDB Endpoint"
        self.mongodb_version = mongodb_version

    @property
    def port(self) -> str:
        """
        The exposed port to the MongoDB endpoint
        """
        return self.get_exposed_port(ENDPOINT_PORT)

    def _configure(self) -> None:
        super()._configure()
        self.with_env("AZURE_COSMOS_EMULATOR_ENABLE_MONGODB_ENDPOINT", self.mongodb_version)
