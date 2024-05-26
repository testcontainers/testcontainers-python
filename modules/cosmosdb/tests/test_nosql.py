import pytest
from testcontainers.cosmosdb import CosmosDBNoSQLEndpointContainer

def test_runs():
    with CosmosDBNoSQLEndpointContainer(partition_count=1, bind_ports=False) as emulator:
        assert emulator.get_exposed_port(8081) is not None, "The NoSQL endpoint's port should be exposed"
