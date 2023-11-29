import pytest

from typing import List, Optional, Set
from testcontainers.core.container import DockerContainer
from testcontainers.modules.cosmosdb import CosmosDBEmulatorContainer


@pytest.fixture(scope="session")
def cosmos_db_container():
    cosmos_db_container = CosmosDBEmulatorContainer()
    cosmos_db_container.start()
    yield cosmos_db_container
    cosmos_db_container.stop()

def test_cosmos_db_connection(cosmos_db_container):
    # Connect to the Cosmos DB emulator
    connection_string = cosmos_db_container.get_connection_url()
    print(connection_string)

    # Write some data to the Cosmos DB container
    # ...

    # Read some data from the Cosmos DB container
    # ...