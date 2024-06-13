import pytest
from pymilvus import MilvusClient

from testcontainers.milvus import MilvusContainer

VERSIONS = ["v2.4.0", "v2.4.4"]


class ClientMilvusContainer(MilvusContainer):
    def get_client(self, *, dbname: str = "default", token: str = "root:Milvus") -> MilvusClient:
        connection_url = self.get_connection_url()
        client = MilvusClient(uri=connection_url, dbname=dbname, token=token)
        return client


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
    test_collection = "test_collection"

    with ClientMilvusContainer(image=image) as milvus_container:
        client = milvus_container.get_client()
        client.create_collection(test_collection, dimension=2)
        collections = client.list_collections()
        assert test_collection in collections

        client.drop_collection(test_collection)
        assert not client.has_collection(test_collection)
