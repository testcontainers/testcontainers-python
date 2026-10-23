import uuid

import pytest

from testcontainers.community.couchbase import CouchbaseContainer


def test_docker_run_couchbase_default_collection():
    with CouchbaseContainer() as couchbase:
        cluster = couchbase.client()
        collection = cluster.bucket("default").default_collection()
        key = uuid.uuid4().hex
        collection.upsert(key, {"hello": "world"})
        assert collection.get(key).content_as[dict] == {"hello": "world"}


# The versions below should reflect the latest Community Edition releases
@pytest.mark.parametrize("image", ["couchbase/server:community-7.6.2", "couchbase/server:community-8.0.2"])
def test_docker_run_couchbase_custom_keyspace(image):
    with CouchbaseContainer(
        image,
        username="administrator",
        password="secret-password",
        bucket="mybucket",
        scope="myscope",
        collection="mycollection",
    ) as couchbase:
        cluster = couchbase.client()
        collection = cluster.bucket("mybucket").scope("myscope").collection("mycollection")
        key = uuid.uuid4().hex
        collection.upsert(key, {"hello": "world"})
        assert collection.get(key).content_as[dict] == {"hello": "world"}

        rows = cluster.query("SELECT RAW 1 + 1").rows()
        assert list(rows) == [2]
