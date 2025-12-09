import uuid

import pytest

from testcontainers.couchbase import CouchbaseContainer


# The versions below should reflect the latest stable releases
@pytest.mark.parametrize("version", ["7.17.18", "8.12.2"])
def test_docker_run_couchbase(version):
    username = "administrator"
    password = "password"
    bucket_name = "mybucket"
    scope_name = "myscope"
    collection_name = "mycollection"

    with CouchbaseContainer(
        username=username, password=password, bucket=bucket_name, scope=scope_name, collection=collection_name
    ) as couchbase_container:
        cluster = couchbase_container.client()
        collection = cluster.bucket(bucket_name=bucket_name).scope(name=scope_name).collection(name=collection_name)
        key = uuid.uuid4().hex
        value = "world"
        doc = {
            "hello": value,
        }
        collection.upsert(key=key, value=doc)
        returned_doc = collection.get(key=key)
        assert returned_doc.value["hello"] == value
