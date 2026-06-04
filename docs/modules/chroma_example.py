import chromadb
from chromadb.config import Settings

from testcontainers.chroma import ChromaContainer


def basic_example():
    with ChromaContainer() as chroma:
        # Get connection URL
        connection_url = chroma.get_connection_url()

        # Create Chroma client
        client = chromadb.HttpClient(host=connection_url, settings=Settings(allow_reset=True))

        # Create a collection
        collection_name = "test_collection"
        collection = client.create_collection(name=collection_name)
        print(f"Created collection: {collection_name}")

        # Add documents and embeddings
        documents = [
            "This is a test document about AI",
            "Machine learning is a subset of AI",
            "Deep learning uses neural networks",
        ]

        embeddings = [
            [0.1, 0.2, 0.3],  # Simple example embeddings
            [0.2, 0.3, 0.4],
            [0.3, 0.4, 0.5],
        ]

        ids = ["doc1", "doc2", "doc3"]
        metadatas = [
            {"source": "test1", "category": "AI"},
            {"source": "test2", "category": "ML"},
            {"source": "test3", "category": "DL"},
        ]

        collection.add(documents=documents, embeddings=embeddings, ids=ids, metadatas=metadatas)
        print("Added documents to collection")

        # Query the collection
        results = collection.query(query_embeddings=[[0.1, 0.2, 0.3]], n_results=2)

        print("\nQuery results:")
        print(f"Documents: {results['documents'][0]}")
        print(f"Distances: {results['distances'][0]}")
        print(f"Metadatas: {results['metadatas'][0]}")

        # Get collection info
        collection_info = client.get_collection(collection_name)
        print("\nCollection info:")
        print(f"Name: {collection_info.name}")
        print(f"Count: {collection_info.count()}")

        # List all collections
        collections = client.list_collections()
        print("\nAvailable collections:")
        for coll in collections:
            print(f"- {coll.name}")


if __name__ == "__main__":
    basic_example()
