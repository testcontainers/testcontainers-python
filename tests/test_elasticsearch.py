import json
import urllib

from testcontainers.elasticsearch import ElasticSearchContainer


def test_docker_run_elasticsearch():
    version = '7.16.1'
    with ElasticSearchContainer(f'elasticsearch:{version}') as es:
        resp = urllib.request.urlopen(es.get_url())
        assert json.loads(resp.read().decode())['version']['number'] == version
