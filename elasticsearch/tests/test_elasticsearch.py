import json
import urllib
import pytest

from testcontainers.elasticsearch import ElasticSearchContainer


# The versions below should reflect the latest stable releases of maintained versions
@pytest.mark.parametrize('version', ['7.17.10', '8.7.1'])
def test_docker_run_elasticsearch(version):
    with ElasticSearchContainer(f'elasticsearch:{version}') as es:
        resp = urllib.request.urlopen(es.get_url())
        assert json.loads(resp.read().decode())['version']['number'] == version
