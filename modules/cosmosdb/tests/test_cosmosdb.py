import pytest
from testcontainers.cosmosdb import CosmosDBEmulatorContainer, Endpoints


def test_docker_run():
    with CosmosDBEmulatorContainer(partition_count=1) as cosmosdb:
        list(cosmosdb.insecure_sync_client().list_databases())
        assert cosmosdb.certificate_pem is not None


def test_enabling_mondogb_endpoint_requires_a_version():
    with pytest.raises(AssertionError, match="A MongoDB version is required to use the MongoDB Endpoint"):
        CosmosDBEmulatorContainer(endpoints=[Endpoints.MongoDB])

    # instanciates
    CosmosDBEmulatorContainer(endpoints=[Endpoints.MongoDB], mongodb_version="4.0")


def test_enables_mondogb_endpoint():
    with CosmosDBEmulatorContainer(partition_count=1, endpoints=[Endpoints.MongoDB], mongodb_version="4.0") as emulator:
        assert emulator.env["AZURE_COSMOS_EMULATOR_ENABLE_MONGODB_ENDPOINT"] == "4.0"
        assert emulator.get_exposed_port(10255) is not None, "The MongoDB endpoint's port should be exposed"
