from testcontainers.couchbase import CouchbaseContainer

# Initialize Couchbase container
with CouchbaseContainer(
    username="administrator", password="password", bucket="mybucket", scope="myscope", collection="mycollection"
) as couchbase:
    # Get a client
    cluster = couchbase.client()

    # Get a collection
    collection = cluster.bucket("mybucket").scope("myscope").collection("mycollection")

    # Upsert a document
    collection.upsert("hello", {"world": "from python"})

    # Get a document
    result = collection.get("hello")
    print(result.value)
