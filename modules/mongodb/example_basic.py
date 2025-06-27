import json
from datetime import datetime

from pymongo import MongoClient

from testcontainers.mongodb import MongoDbContainer


def basic_example():
    with MongoDbContainer() as mongodb:
        # Get connection URL
        connection_url = mongodb.get_connection_url()

        # Create MongoDB client
        client = MongoClient(connection_url)
        print("Connected to MongoDB")

        # Get database and collection
        db = client.test_db
        collection = db.test_collection

        # Insert test documents
        test_docs = [
            {"name": "test1", "value": 100, "category": "A", "created_at": datetime.utcnow()},
            {"name": "test2", "value": 200, "category": "B", "created_at": datetime.utcnow()},
            {"name": "test3", "value": 300, "category": "A", "created_at": datetime.utcnow()},
        ]

        result = collection.insert_many(test_docs)
        print(f"Inserted {len(result.inserted_ids)} documents")

        # Query documents
        print("\nQuery results:")
        for doc in collection.find({"category": "A"}):
            print(json.dumps(doc, default=str, indent=2))

        # Execute aggregation pipeline
        pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "avg_value": {"$avg": "$value"},
                    "count": {"$sum": 1},
                    "min_value": {"$min": "$value"},
                    "max_value": {"$max": "$value"},
                }
            },
            {"$sort": {"avg_value": -1}},
        ]

        print("\nAggregation results:")
        for result in collection.aggregate(pipeline):
            print(json.dumps(result, default=str, indent=2))

        # Create indexes
        collection.create_index("name")
        collection.create_index([("category", 1), ("value", -1)])
        print("\nCreated indexes")

        # List indexes
        print("\nIndexes:")
        for index in collection.list_indexes():
            print(json.dumps(index, default=str, indent=2))

        # Update documents
        result = collection.update_many({"category": "A"}, {"$set": {"updated": True}})
        print(f"\nUpdated {result.modified_count} documents")

        # Find updated documents
        print("\nUpdated documents:")
        for doc in collection.find({"updated": True}):
            print(json.dumps(doc, default=str, indent=2))

        # Delete documents
        result = collection.delete_many({"category": "B"})
        print(f"\nDeleted {result.deleted_count} documents")

        # Get collection stats
        stats = db.command("collstats", "test_collection")
        print("\nCollection stats:")
        print(json.dumps(stats, default=str, indent=2))


if __name__ == "__main__":
    basic_example()
