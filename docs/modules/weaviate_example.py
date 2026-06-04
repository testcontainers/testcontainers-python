import json
from datetime import datetime

import weaviate

from testcontainers.weaviate import WeaviateContainer


def basic_example():
    with WeaviateContainer() as weaviate_container:
        # Get connection parameters
        host = weaviate_container.get_container_host_ip()
        port = weaviate_container.get_exposed_port(weaviate_container.port)

        # Create Weaviate client
        client = weaviate.Client(
            url=f"http://{host}:{port}", auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_container.api_key)
        )
        print("Connected to Weaviate")

        # Create schema
        schema = {
            "classes": [
                {
                    "class": "Article",
                    "description": "A class for news articles",
                    "vectorizer": "text2vec-transformers",
                    "properties": [
                        {"name": "title", "dataType": ["text"], "description": "The title of the article"},
                        {"name": "content", "dataType": ["text"], "description": "The content of the article"},
                        {"name": "category", "dataType": ["text"], "description": "The category of the article"},
                        {"name": "publishedAt", "dataType": ["date"], "description": "When the article was published"},
                    ],
                }
            ]
        }

        client.schema.create(schema)
        print("Created schema")

        # Add objects
        articles = [
            {
                "title": "AI Breakthrough in Natural Language Processing",
                "content": "Researchers have made significant progress in understanding and generating human language.",
                "category": "Technology",
                "publishedAt": datetime.utcnow().isoformat(),
            },
            {
                "title": "New Study Shows Benefits of Exercise",
                "content": "Regular physical activity has been linked to improved mental health and longevity.",
                "category": "Health",
                "publishedAt": datetime.utcnow().isoformat(),
            },
            {
                "title": "Global Climate Summit Reaches Agreement",
                "content": "World leaders have agreed on new measures to combat climate change.",
                "category": "Environment",
                "publishedAt": datetime.utcnow().isoformat(),
            },
        ]

        for article in articles:
            client.data_object.create(data_object=article, class_name="Article")
        print("Added test articles")

        # Query objects
        result = client.query.get("Article", ["title", "category", "publishedAt"]).do()
        print("\nAll articles:")
        print(json.dumps(result, indent=2))

        # Semantic search
        semantic_result = (
            client.query.get("Article", ["title", "content", "category"])
            .with_near_text({"concepts": ["artificial intelligence"]})
            .with_limit(2)
            .do()
        )
        print("\nSemantic search results:")
        print(json.dumps(semantic_result, indent=2))

        # Filtered search
        filtered_result = (
            client.query.get("Article", ["title", "category"])
            .with_where({"path": ["category"], "operator": "Equal", "valueText": "Technology"})
            .do()
        )
        print("\nFiltered search results:")
        print(json.dumps(filtered_result, indent=2))

        # Create cross-reference
        cross_ref_schema = {
            "classes": [
                {
                    "class": "Author",
                    "description": "A class for article authors",
                    "vectorizer": "text2vec-transformers",
                    "properties": [
                        {"name": "name", "dataType": ["text"], "description": "The name of the author"},
                        {"name": "writes", "dataType": ["Article"], "description": "Articles written by the author"},
                    ],
                }
            ]
        }

        client.schema.create(cross_ref_schema)
        print("\nCreated cross-reference schema")

        # Add author with cross-reference
        author_uuid = client.data_object.create(data_object={"name": "John Doe"}, class_name="Author")

        article_uuid = result["data"]["Get"]["Article"][0]["_additional"]["id"]
        client.data_object.reference.add(
            from_uuid=author_uuid,
            from_property_name="writes",
            to_uuid=article_uuid,
            from_class_name="Author",
            to_class_name="Article",
        )
        print("Added author with cross-reference")

        # Query with cross-reference
        cross_ref_result = (
            client.query.get("Author", ["name"])
            .with_additional(["id"])
            .with_references({"writes": {"properties": ["title", "category"]}})
            .do()
        )
        print("\nCross-reference query results:")
        print(json.dumps(cross_ref_result, indent=2))

        # Create aggregation
        agg_result = client.query.aggregate("Article").with_fields("category").with_meta_count().do()
        print("\nAggregation results:")
        print(json.dumps(agg_result, indent=2))

        # Clean up
        client.schema.delete_all()
        print("\nCleaned up schema")


if __name__ == "__main__":
    basic_example()
