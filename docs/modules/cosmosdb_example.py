import json

from azure.cosmos import CosmosClient, PartitionKey

from testcontainers.cosmosdb import CosmosDbContainer


def basic_example():
    with CosmosDbContainer() as cosmos:
        # Get connection parameters
        endpoint = cosmos.get_connection_url()
        key = cosmos.get_primary_key()

        # Create CosmosDB client
        client = CosmosClient(endpoint, key)

        # Create a database
        database_name = "test_database"
        database = client.create_database_if_not_exists(id=database_name)
        print(f"Created database: {database_name}")

        # Create a container
        container_name = "test_container"
        container = database.create_container_if_not_exists(
            id=container_name, partition_key=PartitionKey(path="/category")
        )
        print(f"Created container: {container_name}")

        # Insert test items
        test_items = [
            {"id": "1", "category": "test1", "name": "Item 1", "value": 100},
            {"id": "2", "category": "test2", "name": "Item 2", "value": 200},
            {"id": "3", "category": "test1", "name": "Item 3", "value": 300},
        ]

        for item in test_items:
            container.create_item(body=item)
        print("Inserted test items")

        # Query items
        query = "SELECT * FROM c WHERE c.category = 'test1'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        print("\nQuery results:")
        for item in items:
            print(json.dumps(item, indent=2))

        # Execute a more complex query
        query = """
        SELECT
            c.category,
            COUNT(1) as count,
            AVG(c.value) as avg_value,
            MIN(c.value) as min_value,
            MAX(c.value) as max_value
        FROM c
        GROUP BY c.category
        """

        results = list(container.query_items(query=query, enable_cross_partition_query=True))

        print("\nAggregation results:")
        for result in results:
            print(json.dumps(result, indent=2))

        # Get container info
        container_properties = container.read()
        print("\nContainer properties:")
        print(f"ID: {container_properties['id']}")
        print(f"Partition Key: {container_properties['partitionKey']}")
        print(f"Indexing Policy: {json.dumps(container_properties['indexingPolicy'], indent=2)}")


if __name__ == "__main__":
    basic_example()
