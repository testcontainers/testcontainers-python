import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.modules.cosmosdb import CosmosDBEmulatorContainer

@pytest.fixture(scope="session")
def cosmosdb_container() -> DockerContainer:
    with CosmosDBEmulatorContainer("mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest") as cosmosdb:
        cosmosdb.start()
        yield cosmosdb

@pytest.mark.usefixtures("cosmosdb_container")
def test_cosmosdb_connection(cosmosdb_container):
    # Use the Cosmos DB emulator endpoint and key to connect to the database
    endpoint = cosmosdb_container.get_emulator_endpoint()
    key = cosmosdb_container.get_emulator_key()

    # Connect to the Cosmos DB emulator
    cosmos_client = CosmosClient(endpoint, key)

    # Create a new database and container
    database = cosmos_client.create_database_if_not_exists("test")
    container = database.create_container_if_not_exists("test")

    # Write a document to the container
    container.create_item({"id": "1", "name": "John Doe"})

    # Read the document from the container
    document = container.read_item("1")

    # Assert that the document was read correctly
    assert document["id"] == "1"
    assert document["name"] == "John Doe"