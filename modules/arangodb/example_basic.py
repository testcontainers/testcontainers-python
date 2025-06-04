import json

from arango import ArangoClient

from testcontainers.arangodb import ArangoDbContainer


def basic_example():
    with ArangoDbContainer() as arango:
        # Get connection parameters
        host = arango.get_container_host_ip()
        port = arango.get_exposed_port(arango.port)
        username = arango.username
        password = arango.password

        # Create ArangoDB client
        client = ArangoClient(hosts=f"http://{host}:{port}")
        db = client.db("_system", username=username, password=password)
        print("Connected to ArangoDB")

        # Create a test database
        db_name = "test_db"
        if not db.has_database(db_name):
            db.create_database(db_name)
            print(f"Created database: {db_name}")

        # Switch to test database
        test_db = client.db(db_name, username=username, password=password)

        # Create a test collection
        collection_name = "test_collection"
        if not test_db.has_collection(collection_name):
            test_db.create_collection(collection_name)
            print(f"Created collection: {collection_name}")

        collection = test_db.collection(collection_name)

        # Insert test documents
        test_docs = [
            {"_key": "1", "name": "test1", "value": 100, "category": "A"},
            {"_key": "2", "name": "test2", "value": 200, "category": "B"},
            {"_key": "3", "name": "test3", "value": 300, "category": "A"},
        ]

        collection.import_bulk(test_docs)
        print("Inserted test documents")

        # Query documents
        cursor = test_db.aql.execute("""
            FOR doc IN test_collection
            FILTER doc.category == "A"
            RETURN doc
        """)

        print("\nQuery results:")
        for doc in cursor:
            print(json.dumps(doc, indent=2))

        # Execute a more complex query
        cursor = test_db.aql.execute("""
            FOR doc IN test_collection
            COLLECT category = doc.category
            AGGREGATE
                count = COUNT(1),
                avg_value = AVG(doc.value),
                min_value = MIN(doc.value),
                max_value = MAX(doc.value)
            RETURN {
                category: category,
                count: count,
                avg_value: avg_value,
                min_value: min_value,
                max_value: max_value
            }
        """)

        print("\nAggregation results:")
        for result in cursor:
            print(json.dumps(result, indent=2))

        # Get collection info
        collection_info = collection.properties()
        print("\nCollection properties:")
        print(f"Name: {collection_info['name']}")
        print(f"Type: {collection_info['type']}")
        print(f"Status: {collection_info['status']}")
        print(f"Count: {collection.count()}")


if __name__ == "__main__":
    basic_example()
