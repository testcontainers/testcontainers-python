import json
import urllib.request

import pytest

from testcontainers.elasticsearch import ElasticSearchContainer


# The versions below should reflect the latest stable releases
@pytest.mark.parametrize("version", ["7.17.18", "8.12.2"])
def test_docker_run_elasticsearch(version):
    with ElasticSearchContainer(f"elasticsearch:{version}", mem_limit="3G") as es:
        resp = urllib.request.urlopen(f"http://{es.get_container_host_ip()}:{es.get_exposed_port(es.port)}")
        assert json.loads(resp.read().decode())["version"]["number"] == version
