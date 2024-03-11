import pytest
from testcontainers.qdrant import QdrantContainer
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from grpc import RpcError
from pathlib import Path


def test_docker_run_qdrant():
    with QdrantContainer() as qdrant:
        client = qdrant.get_client()
        collections = client.get_collections().collections
        assert len(collections) == 0

        client = qdrant.get_client(prefer_grpc=True)
        collections = client.get_collections().collections
        assert len(collections) == 0


def test_qdrant_with_api_key_http():
    api_key = uuid.uuid4().hex

    with QdrantContainer(container_api_key=api_key) as qdrant:
        with pytest.raises(UnexpectedResponse) as e:
            QdrantClient(location=f"http://{qdrant.http_host_address}").get_collections()

        assert "Invalid api-key" in str(e.value)

        collections = (
            QdrantClient(location=f"http://{qdrant.http_host_address}", api_key=api_key).get_collections().collections
        )

        assert len(collections) == 0


def test_qdrant_with_api_key_grpc():
    api_key = uuid.uuid4().hex

    with QdrantContainer(container_api_key=api_key) as qdrant:
        with pytest.raises(RpcError) as e:
            QdrantClient(
                url=f"http://{qdrant.grpc_host_address}",
                grpc_port=qdrant.get_exposed_port(qdrant.grpc_port),
                prefer_grpc=True,
            ).get_collections()

        assert "Invalid api-key" in str(e.value)

        collections = (
            QdrantClient(
                url=f"http://{qdrant.grpc_host_address}",
                grpc_port=qdrant.get_exposed_port(qdrant.grpc_port),
                prefer_grpc=True,
                api_key=api_key,
            )
            .get_collections()
            .collections
        )

        assert len(collections) == 0


def test_qdrant_with_config_file():
    config_file_path = Path(__file__).with_name("test_config.yaml")

    with QdrantContainer(config_file_path=config_file_path) as qdrant:
        with pytest.raises(UnexpectedResponse) as e:
            QdrantClient(location=f"http://{qdrant.http_host_address}").get_collections()

        assert "Invalid api-key" in str(e.value)
