import json
from datetime import datetime

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models

from testcontainers.qdrant import QdrantContainer


def basic_example():
    with QdrantContainer() as qdrant:
        # Get connection parameters
        host = qdrant.get_container_host_ip()
        port = qdrant.get_exposed_port(qdrant.port)

        # Create Qdrant client
        client = QdrantClient(host=host, port=port)
        print("Connected to Qdrant")

        # Create collection
        collection_name = "test_collection"
        vector_size = 128

        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )
        print(f"Created collection: {collection_name}")

        # Generate test vectors and payloads
        num_vectors = 5
        vectors = np.random.rand(num_vectors, vector_size).tolist()

        payloads = [
            {
                "text": "AI and machine learning are transforming industries",
                "category": "Technology",
                "tags": ["AI", "ML", "innovation"],
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "text": "New study reveals benefits of meditation",
                "category": "Health",
                "tags": ["wellness", "mental health"],
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "text": "Global warming reaches critical levels",
                "category": "Environment",
                "tags": ["climate", "sustainability"],
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "text": "Stock market shows strong growth",
                "category": "Finance",
                "tags": ["investing", "markets"],
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "text": "New restaurant opens in downtown",
                "category": "Food",
                "tags": ["dining", "local"],
                "timestamp": datetime.utcnow().isoformat(),
            },
        ]

        # Upload vectors with payloads
        client.upsert(
            collection_name=collection_name,
            points=models.Batch(ids=list(range(num_vectors)), vectors=vectors, payloads=payloads),
        )
        print("Uploaded vectors with payloads")

        # Search vectors
        search_result = client.search(collection_name=collection_name, query_vector=vectors[0], limit=3)
        print("\nSearch results:")
        for scored_point in search_result:
            print(
                json.dumps(
                    {"id": scored_point.id, "score": scored_point.score, "payload": scored_point.payload}, indent=2
                )
            )

        # Filtered search
        filter_result = client.search(
            collection_name=collection_name,
            query_vector=vectors[0],
            query_filter=models.Filter(
                must=[models.FieldCondition(key="category", match=models.MatchValue(value="Technology"))]
            ),
            limit=2,
        )
        print("\nFiltered search results:")
        for scored_point in filter_result:
            print(
                json.dumps(
                    {"id": scored_point.id, "score": scored_point.score, "payload": scored_point.payload}, indent=2
                )
            )

        # Create payload index
        client.create_payload_index(
            collection_name=collection_name, field_name="category", field_schema=models.PayloadFieldSchema.KEYWORD
        )
        print("\nCreated payload index on category field")

        # Create vector index
        client.create_payload_index(
            collection_name=collection_name, field_name="tags", field_schema=models.PayloadFieldSchema.KEYWORD
        )
        print("Created payload index on tags field")

        # Scroll through collection
        scroll_result = client.scroll(collection_name=collection_name, limit=10, with_payload=True, with_vectors=True)
        print("\nScrolled through collection:")
        for point in scroll_result[0]:
            print(json.dumps({"id": point.id, "payload": point.payload}, indent=2))

        # Get collection info
        collection_info = client.get_collection(collection_name)
        print("\nCollection info:")
        print(
            json.dumps(
                {
                    "name": collection_info.name,
                    "vectors_count": collection_info.vectors_count,
                    "points_count": collection_info.points_count,
                    "status": collection_info.status,
                },
                indent=2,
            )
        )

        # Update payload
        client.set_payload(collection_name=collection_name, payload={"new_field": "updated value"}, points=[0, 1])
        print("\nUpdated payload for points 0 and 1")

        # Delete points
        client.delete(collection_name=collection_name, points_selector=models.PointIdsList(points=[4]))
        print("Deleted point with id 4")

        # Clean up
        client.delete_collection(collection_name)
        print("\nDeleted collection")


if __name__ == "__main__":
    basic_example()
