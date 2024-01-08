from testcontainers.cosmosdb import CosmosDbEmulatorContainer
from azure.cosmos import ContainerProxy


def test_cosmosdb_emulator():

    with CosmosDbEmulatorContainer() as cosmos:

        # Create a new cosmos database as well as container
        container_client: ContainerProxy = cosmos.bootstrap_container(db_name="mydb",
                                                                     container_name="mycontainer",
                                                                     container_partition_key="id")

        # Insert some test data
        container_client.create_item({"id": "1", "name": "sally"})
        container_client.create_item({"id": "2", "name": "paul"})

        # read the newly inserted data
        documents = container_client.read_all_items()

        # we expect: to have retrieved 2 documents
        count: int = 0
        for document in documents:
            count += 1
            assert document['id'] is not None
            assert document['name'] is not None
        assert count == 2