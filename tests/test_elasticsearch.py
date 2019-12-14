import json
import urllib

from testcontainers.elasticsearch import ElasticsearchContainer


def test_docker_run_elasticsearch():
    config = ElasticsearchContainer()
    with config as es:
        resp = urllib.request.urlopen(es.get_url())
        assert json.loads(resp.read().decode())['version']['number'] == '7.5.0'
