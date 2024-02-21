from testcontainers.opensearch import OpenSearchContainer


def test_docker_run_opensearch():
    with OpenSearchContainer() as opensearch:
        client = opensearch.get_client()
        assert client.cluster.health()["status"] == "green"


def test_docker_run_opensearch_with_security():
    with OpenSearchContainer(security_enabled=True) as opensearch:
        client = opensearch.get_client()
        assert client.cluster.health()["status"] == "green"


def test_docker_run_opensearch_v1():
    with OpenSearchContainer(image="opensearchproject/opensearch:1.3.6") as opensearch:
        client = opensearch.get_client()
        assert client.cluster.health()["status"] == "green"


def test_docker_run_opensearch_v1_with_security():
    with OpenSearchContainer(image="opensearchproject/opensearch:1.3.6", security_enabled=True) as opensearch:
        client = opensearch.get_client()
        assert client.cluster.health()["status"] == "green"


def test_search():
    with OpenSearchContainer() as opensearch:
        client = opensearch.get_client()
        client.index(index="test", body={"test": "test"})
        client.indices.refresh(index="test")
        result = client.search(index="test", body={"query": {"match_all": {}}})
        assert result["hits"]["total"]["value"] == 1
