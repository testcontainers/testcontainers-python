import json
from datetime import datetime

import numpy as np
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from testcontainers.milvus import MilvusContainer


def basic_example():
    with MilvusContainer() as milvus:
        # Get connection parameters
        host = milvus.get_container_host_ip()
        port = milvus.get_exposed_port(milvus.port)

        # Connect to Milvus
        connections.connect(alias="default", host=host, port=port)
        print("Connected to Milvus")

        # Create collection
        collection_name = "test_collection"
        dim = 128

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="tags", dtype=DataType.JSON),
            FieldSchema(name="timestamp", dtype=DataType.VARCHAR, max_length=50),
        ]

        schema = CollectionSchema(fields=fields, description="Test collection")
        collection = Collection(name=collection_name, schema=schema)
        print(f"Created collection: {collection_name}")

        # Create index
        index_params = {"metric_type": "COSINE", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}
        collection.create_index(field_name="vector", index_params=index_params)
        print("Created index on vector field")

        # Generate test data
        num_entities = 5
        vectors = np.random.rand(num_entities, dim).tolist()

        texts = [
            "AI and machine learning are transforming industries",
            "New study reveals benefits of meditation",
            "Global warming reaches critical levels",
            "Stock market shows strong growth",
            "New restaurant opens in downtown",
        ]

        categories = ["Technology", "Health", "Environment", "Finance", "Food"]

        tags = [
            ["AI", "ML", "innovation"],
            ["wellness", "mental health"],
            ["climate", "sustainability"],
            ["investing", "markets"],
            ["dining", "local"],
        ]

        timestamps = [datetime.utcnow().isoformat() for _ in range(num_entities)]

        # Insert data
        entities = [vectors, texts, categories, tags, timestamps]

        collection.insert(entities)
        print("Inserted test data")

        # Flush collection
        collection.flush()
        print("Flushed collection")

        # Load collection
        collection.load()
        print("Loaded collection")

        # Search vectors
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}

        results = collection.search(
            data=[vectors[0]],
            anns_field="vector",
            param=search_params,
            limit=3,
            output_fields=["text", "category", "tags"],
        )

        print("\nSearch results:")
        for hits in results:
            for hit in hits:
                print(json.dumps({"id": hit.id, "distance": hit.distance, "entity": hit.entity}, indent=2))

        # Query with filter
        filter_expr = 'category == "Technology"'
        query_results = collection.query(expr=filter_expr, output_fields=["text", "category", "tags"])

        print("\nQuery results with filter:")
        print(json.dumps(query_results, indent=2))

        # Get collection stats
        stats = collection.get_statistics()
        print("\nCollection statistics:")
        print(json.dumps(stats, indent=2))

        # Create partition
        partition_name = "test_partition"
        collection.create_partition(partition_name)
        print(f"\nCreated partition: {partition_name}")

        # List partitions
        partitions = collection.partitions
        print("\nPartitions:")
        for partition in partitions:
            print(
                json.dumps(
                    {"name": partition.name, "is_empty": partition.is_empty, "num_entities": partition.num_entities},
                    indent=2,
                )
            )

        # Delete partition
        collection.drop_partition(partition_name)
        print(f"Deleted partition: {partition_name}")

        # Clean up
        utility.drop_collection(collection_name)
        print("\nDropped collection")

        # Disconnect
        connections.disconnect("default")
        print("Disconnected from Milvus")


if __name__ == "__main__":
    basic_example()
