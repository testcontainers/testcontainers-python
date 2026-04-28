import hashlib
import time

import pytest
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.operations import SearchIndexModel

from testcontainers.mongodb import MongoDbContainer, MongoDBAtlasLocalContainer


@pytest.mark.parametrize("version", ["7.0.7", "6.0.14", "5.0.26"])
def test_docker_run_mongodb(version: str):
    with MongoDbContainer(f"mongo:{version}") as mongo:
        db = mongo.get_connection_client().test
        doc = {
            "address": {
                "street": "2 Avenue",
                "zipcode": "10075",
                "building": "1480",
                "coord": [-73.9557413, 40.7720266],
            },
            "borough": "Manhattan",
            "cuisine": "Italian",
            "name": "Vella",
            "restaurant_id": "41704620",
        }
        result = db.restaurants.insert_one(doc)
        assert result.inserted_id

        cursor = db.restaurants.find({"borough": "Manhattan"})
        assert cursor.next()["restaurant_id"] == doc["restaurant_id"]


# This is a feature in the generic DbContainer class
# but it can't be tested on its own
# so is tested in various database modules:
# - mysql / mariadb
# - postgresql
# - sqlserver
# - mongodb
# - db2
def test_quoted_password():
    user = "root"
    password = "p@$%25+0&%rd :/!=?"
    quoted_password = "p%40%24%2525+0%26%25rd %3A%2F%21%3D%3F"
    # driver = "pymongo"
    kwargs = {
        "username": user,
        "password": password,
    }
    with MongoDbContainer("mongo:7.0.7", **kwargs) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(27017)
        expected_url = f"mongodb://{user}:{quoted_password}@{host}:{port}"
        url = container.get_connection_url()
        assert url == expected_url


def test_docker_run_mongodb_atlas_local():
    with MongoDBAtlasLocalContainer("mongodb/mongodb-atlas-local:8.0.4") as atlas:
        client = atlas.get_connection_client()
        db = client.test
        doc = {"name": "Atlas Test", "value": 42}
        result = db.test_collection.insert_one(doc)
        assert result.inserted_id
        found = db.test_collection.find_one({"name": "Atlas Test"})
        assert found is not None
        assert found["value"] == 42


def test_mongodb_atlas_local_connection_string():
    with MongoDBAtlasLocalContainer("mongodb/mongodb-atlas-local:8.0.4") as atlas:
        conn_str = atlas.get_connection_string()
        assert conn_str.startswith("mongodb://")
        assert "directConnection=true" in conn_str


# ---------------------------------------------------------------------------
# Vector Search
# ---------------------------------------------------------------------------

EMBEDDING_DIM = 16
NUM_DOCS = 5
SENTENCES = [
    "The quick brown fox jumps over the lazy dog",
    "MongoDB Atlas provides powerful search capabilities",
    "Vector search enables semantic similarity matching",
    "Testcontainers make integration testing easy",
    "Python is a versatile programming language",
]


def mock_embedding(text: str) -> list[float]:
    """Deterministic mock embedding: hash the text into a float vector."""
    digest = hashlib.sha256(text.encode()).digest()
    # Take EMBEDDING_DIM bytes and normalise to [0, 1]
    return [b / 255.0 for b in digest[:EMBEDDING_DIM]]


@pytest.fixture(scope="module")
def atlas():
    with MongoDBAtlasLocalContainer("mongodb/mongodb-atlas-local:8.0.4") as container:
        yield container


@pytest.fixture(scope="module")
def indexed_collection(atlas):
    """Insert documents with embeddings, create a vector index, and wait until all docs are indexed."""
    client = atlas.get_connection_client()
    db = client["test_vector"]
    collection = db["documents"]

    # Insert documents
    docs = [{"text": s, "embedding": mock_embedding(s)} for s in SENTENCES]
    collection.insert_many(docs)

    # Create vector search index
    index_definition = {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": EMBEDDING_DIM,
                "similarity": "cosine",
            }
        ]
    }
    collection.create_search_index(
        model=SearchIndexModel(
            definition=index_definition,
            name="vector_index",
            type="vectorSearch",
        )
    )

    # Wait until all documents are indexed by polling $vectorSearch.
    # The index may throw OperationFailure while it is still initialising.
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            results = list(
                collection.aggregate(
                    [
                        {
                            "$vectorSearch": {
                                "index": "vector_index",
                                "path": "embedding",
                                "queryVector": mock_embedding("test"),
                                "numCandidates": NUM_DOCS,
                                "limit": NUM_DOCS,
                            }
                        }
                    ]
                )
            )
        except OperationFailure:
            # Index not yet initialised
            results = []
        if len(results) == NUM_DOCS:
            break
        time.sleep(1)
    else:
        pytest.fail(f"Vector index did not index all {NUM_DOCS} documents within 60s")

    return collection


def test_vector_search(indexed_collection):
    """Search for fewer documents than exist and verify the count."""
    top_k = 3
    query_vector = mock_embedding(SENTENCES[0])
    results = list(
        indexed_collection.aggregate(
            [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embedding",
                        "queryVector": query_vector,
                        "numCandidates": NUM_DOCS,
                        "limit": top_k,
                    }
                },
                {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
            ]
        )
    )
    assert len(results) == top_k
    # The first result should be the sentence itself (exact match → highest score)
    assert results[0]["text"] == SENTENCES[0]
    # All results should have a score
    for doc in results:
        assert 0.0 <= doc["score"] <= 1.0
