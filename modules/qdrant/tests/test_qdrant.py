import pytest
from testcontainers.qdrant import QdrantContainer
import uuid
from grpc import RpcError
from pathlib import Path

import qdrant_client


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

    with QdrantContainer(api_key=api_key) as qdrant:
        with pytest.raises(qdrant_client.http.exceptions.UnexpectedResponse) as e:
            # Construct a client without an API key
            qdrant_client.QdrantClient(location=f"http://{qdrant.rest_host_address}").get_collections()

        assert "Must provide an API key" in str(e.value)

        # Construct a client with an API key
        collections = (
            qdrant_client.QdrantClient(location=f"http://{qdrant.rest_host_address}", api_key=api_key)
            .get_collections()
            .collections
        )

        assert len(collections) == 0

        # Get an automatically configured client instance
        collections = qdrant.get_client().get_collections().collections

        assert len(collections) == 0


def test_qdrant_with_api_key_grpc():
    api_key = uuid.uuid4().hex

    with QdrantContainer(api_key=api_key) as qdrant:
        with pytest.raises(RpcError) as e:
            qdrant_client.QdrantClient(
                url=f"http://{qdrant.grpc_host_address}",
                grpc_port=qdrant.exposed_grpc_port,
                prefer_grpc=True,
            ).get_collections()

        assert "Must provide an API key" in str(e.value)

        collections = (
            qdrant_client.QdrantClient(
                url=f"http://{qdrant.grpc_host_address}",
                grpc_port=qdrant.exposed_grpc_port,
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
        with pytest.raises(qdrant_client.http.exceptions.UnexpectedResponse) as e:
            qdrant_client.QdrantClient(location=f"http://{qdrant.rest_host_address}").get_collections()

        assert "Must provide an API key" in str(e.value)
