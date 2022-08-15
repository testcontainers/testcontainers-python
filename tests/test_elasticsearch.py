import json
import urllib
import pytest

from testcontainers.elasticsearch import ElasticSearchContainer


# The versions below were the current supported versions at time of writing (2022-08-11)
@pytest.mark.parametrize('version', ['6.8.23', '7.17.5', '8.3.3'])
def test_docker_run_elasticsearch(version):
    with ElasticSearchContainer(f'elasticsearch:{version}') as es:
        resp = urllib.request.urlopen(es.get_url())
        assert json.loads(resp.read().decode())['version']['number'] == version
