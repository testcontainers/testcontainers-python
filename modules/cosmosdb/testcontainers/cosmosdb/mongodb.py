import os
from ._emulator import CosmosDBEmulatorContainer

__all__ = ["MongoDBEmulatorContainer"]

ENDPOINT_PORT = 10255

class MongoDBEmulatorContainer(CosmosDBEmulatorContainer):
    """
    CosmosDB MongoDB enpoint Emulator.

    Example:

        .. doctest::
                >>> from testcontainers.cosmosdb import MongoDBEmulatorContainer
                >>> with CosmosDBEmulatorContainer(mongodb_version="4.0") as emulator:
                ...    print(f"Point yout MongoDB client to {emulator.host}:{emulator.port}}")
    """

    def __init__(
        self,
        mongodb_version: str = None,
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
        return self.get_exposed_port(ENDPOINT_PORT)
    
    def _configure(self) -> None:
        super()._configure()
        self.with_env("AZURE_COSMOS_EMULATOR_ENABLE_MONGODB_ENDPOINT", self.mongodb_version)
