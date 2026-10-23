from testcontainers.community.couchbase import CouchbaseContainer


def basic_example():
    # Starts a single-node Couchbase Server (Community Edition) cluster with the
    # Data, Query, Index and Search services, and creates the given keyspace.
    with CouchbaseContainer(bucket="mybucket", scope="myscope", collection="mycollection") as couchbase:
        cluster = couchbase.client()
        collection = cluster.bucket("mybucket").scope("myscope").collection("mycollection")

        # Key-value operations
        collection.upsert("user::1", {"name": "Alice", "city": "Bengaluru"})
        print(collection.get("user::1").content_as[dict])

        # SQL++ query
        for row in cluster.query("SELECT RAW 1 + 1"):
            print(row)


def custom_image_example():
    # Any Couchbase Server image can be used, e.g. the Enterprise Edition
    with CouchbaseContainer("couchbase/server:enterprise-8.0.0") as couchbase:
        print(couchbase.get_connection_url())


if __name__ == "__main__":
    basic_example()
