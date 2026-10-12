import pytest
from meilisearch import Client
from meilisearch.errors import MeilisearchApiError

from testcontainers.community.meilisearch import MeilisearchContainer


def test_docker_run_meilisearch():
    with MeilisearchContainer() as meili:
        client = Client(meili.get_connection_url(), meili.get_master_key())

        assert client.health()["status"] == "available"

        index = client.index("movies")
        task = index.add_documents([{"id": 1, "title": "Movie"}])
        client.wait_for_task(task.task_uid)

        assert index.search("Movie")["hits"][0]["id"] == 1


def test_docker_run_meilisearch_requires_master_key():
    with MeilisearchContainer() as meili:
        client = Client(meili.get_connection_url())

        with pytest.raises(MeilisearchApiError):
            client.get_keys()


def test_meilisearch_rejects_short_master_key_in_production():
    with pytest.raises(ValueError):
        MeilisearchContainer(master_key="short")


def test_meilisearch_allows_short_master_key_in_development():
    container = MeilisearchContainer(meili_env="development", master_key="short")
    assert container.get_master_key() == "short"
