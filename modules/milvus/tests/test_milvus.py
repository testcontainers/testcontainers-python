import pytest

from testcontainers.milvus import MilvusContainer

VERSIONS = ["v2.4.0", "v2.4.1", "v2.4.3", "v2.4.4", "latest"]


@pytest.mark.parametrize("version", VERSIONS)
def test_run_milvus_success(version: str):
    image = f"milvusdb/milvus:{version}"

    with MilvusContainer(image=image) as milvus_container:
        exposed_port = milvus_container.get_exposed_port(milvus_container.port)
        url = milvus_container.get_connection_url()

    assert url and exposed_port in url


@pytest.mark.parametrize("version", VERSIONS)
def test_milvus_client_success(version: str):
    image = f"milvusdb/milvus:{version}"
    test_collection = 'test_collection'

    with MilvusContainer(image=image) as milvus_container:
        client = milvus_container.get_client()
        client.create_collection(test_collection, dimension=2)
        collections = client.list_collections()
        assert test_collection in collections

        client.drop_collection(test_collection)
        assert not client.has_collection(test_collection)
