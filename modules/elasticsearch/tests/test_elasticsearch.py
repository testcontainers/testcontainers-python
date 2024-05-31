import json
import urllib.request

import pytest

from testcontainers.elasticsearch import ElasticSearchContainer


# The versions below should reflect the latest stable releases
@pytest.mark.parametrize("version", ["7.17.18", "8.12.2"])
def test_docker_run_elasticsearch(version):
    with ElasticSearchContainer(f"elasticsearch:{version}", mem_limit="3G") as es:
        resp = urllib.request.urlopen(es.get_url())
        assert json.loads(resp.read().decode())["version"]["number"] == version


@pytest.mark.parametrize("version", ["7.17.18", "8.12.2"])
def test_docker_run_elasticsearch_custom_port(version):
    with ElasticSearchContainer(f"elasticsearch:{version}", mem_limit="3G", port=9876) as es:
        resp = urllib.request.urlopen(es.get_url())
        assert json.loads(resp.read().decode())["version"]["number"] == version
