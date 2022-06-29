import json
import urllib

from testcontainers.opensearch import OpenSearchContainer


def test_docker_run_opensearch():
    version = 'latest'
    with OpenSearchContainer(f'opensearchproject/opensearch:{version}') as osearch:
        resp = urllib.request.urlopen(osearch.get_url())
        assert json.loads(resp.read().decode())['version']['number'] == version
