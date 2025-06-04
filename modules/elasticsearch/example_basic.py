import json
from datetime import datetime

from elasticsearch import Elasticsearch

from testcontainers.elasticsearch import ElasticsearchContainer


def basic_example():
    with ElasticsearchContainer() as elasticsearch:
        # Get connection parameters
        host = elasticsearch.get_container_host_ip()
        port = elasticsearch.get_exposed_port(elasticsearch.port)

        # Create Elasticsearch client
        es = Elasticsearch(f"http://{host}:{port}")
        print("Connected to Elasticsearch")

        # Create index
        index_name = "test_index"
        index_settings = {
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "value": {"type": "integer"},
                    "category": {"type": "keyword"},
                    "created_at": {"type": "date"},
                }
            },
        }

        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name, body=index_settings)
            print(f"Created index: {index_name}")

        # Insert test documents
        test_docs = [
            {"name": "test1", "value": 100, "category": "A", "created_at": datetime.utcnow()},
            {"name": "test2", "value": 200, "category": "B", "created_at": datetime.utcnow()},
            {"name": "test3", "value": 300, "category": "A", "created_at": datetime.utcnow()},
        ]

        for i, doc in enumerate(test_docs, 1):
            es.index(index=index_name, id=i, document=doc)
        print("Inserted test documents")

        # Refresh index
        es.indices.refresh(index=index_name)

        # Search documents
        search_query = {"query": {"bool": {"must": [{"term": {"category": "A"}}]}}}

        print("\nSearch results:")
        response = es.search(index=index_name, body=search_query)
        for hit in response["hits"]["hits"]:
            print(json.dumps(hit["_source"], default=str, indent=2))

        # Execute aggregation
        agg_query = {
            "size": 0,
            "aggs": {
                "categories": {
                    "terms": {"field": "category"},
                    "aggs": {
                        "avg_value": {"avg": {"field": "value"}},
                        "min_value": {"min": {"field": "value"}},
                        "max_value": {"max": {"field": "value"}},
                    },
                }
            },
        }

        print("\nAggregation results:")
        response = es.search(index=index_name, body=agg_query)
        for bucket in response["aggregations"]["categories"]["buckets"]:
            print(f"\nCategory: {bucket['key']}")
            print(f"Count: {bucket['doc_count']}")
            print(f"Avg value: {bucket['avg_value']['value']:.2f}")
            print(f"Min value: {bucket['min_value']['value']}")
            print(f"Max value: {bucket['max_value']['value']}")

        # Update document
        update_body = {"doc": {"value": 150, "updated_at": datetime.utcnow()}}
        es.update(index=index_name, id=1, body=update_body)
        print("\nUpdated document")

        # Get document
        doc = es.get(index=index_name, id=1)
        print("\nUpdated document:")
        print(json.dumps(doc["_source"], default=str, indent=2))

        # Delete document
        es.delete(index=index_name, id=2)
        print("\nDeleted document")

        # Get index stats
        stats = es.indices.stats(index=index_name)
        print("\nIndex stats:")
        print(f"Documents: {stats['indices'][index_name]['total']['docs']['count']}")
        print(f"Size: {stats['indices'][index_name]['total']['store']['size_in_bytes']} bytes")


if __name__ == "__main__":
    basic_example()
