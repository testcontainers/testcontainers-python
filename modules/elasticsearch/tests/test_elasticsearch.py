import json
import urllib.request

import pytest

from testcontainers.core.utils import is_arm
from testcontainers.elasticsearch import ElasticSearchContainer


# The versions below should reflect the latest stable releases
@pytest.mark.parametrize("version", ["7.17.18", "8.12.2"])
@pytest.mark.skipif(is_arm(), reason="db2 container not available for ARM")
def test_docker_run_elasticsearch(version):
    with ElasticSearchContainer(f"elasticsearch:{version}", mem_limit="3G") as es:
        resp = urllib.request.urlopen(es.get_url())
        assert json.loads(resp.read().decode())["version"]["number"] == version
