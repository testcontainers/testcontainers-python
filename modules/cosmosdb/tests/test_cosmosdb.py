import pytest
from testcontainers.cosmosdb import CosmosDBEmulatorContainer

def test_docker_run():
	with CosmosDBEmulatorContainer(partition_count=1) as cosmosdb:
		list(cosmosdb.sync_client().list_databases())
