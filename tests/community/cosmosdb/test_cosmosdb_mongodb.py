import pytest
from testcontainers.cosmosdb import CosmosDBMongoEndpointContainer


def test_requires_a_version():
    with pytest.raises(AssertionError, match="A MongoDB version is required"):
        CosmosDBMongoEndpointContainer(mongodb_version=None)

    # instanciates
    CosmosDBMongoEndpointContainer(mongodb_version="4.0")


def test_runs():
    with CosmosDBMongoEndpointContainer(mongodb_version="4.0", partition_count=1, bind_ports=False) as emulator:
        assert emulator.env["AZURE_COSMOS_EMULATOR_ENABLE_MONGODB_ENDPOINT"] == "4.0"
        assert emulator.get_exposed_port(10255) is not None, "The MongoDB endpoint's port should be exposed"
