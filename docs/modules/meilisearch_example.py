from meilisearch import Client

from testcontainers.community.meilisearch import MeilisearchContainer


def basic_example():
    with MeilisearchContainer() as meili:
        client = Client(meili.get_connection_url(), meili.get_master_key())

        print(f"Health: {client.health()['status']}")

        index = client.index("movies")

        documents = [
            {"id": 1, "title": "Interstellar", "genre": "sci-fi"},
            {"id": 2, "title": "Arrival", "genre": "sci-fi"},
            {"id": 3, "title": "The Grand Budapest Hotel", "genre": "comedy"},
        ]

        task = index.add_documents(documents)
        client.wait_for_task(task.task_uid)
        print(f"Indexed {len(documents)} documents")

        results = index.search("interstelar")
        print("\nSearch results (typo-tolerant):")
        for hit in results["hits"]:
            print(f"  {hit['id']}: {hit['title']}")

        results = index.search("", {"filter": None, "limit": 2})
        print(f"\nTotal hits with empty query: {len(results['hits'])}")


if __name__ == "__main__":
    basic_example()
