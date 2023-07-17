import json
import urllib

import pytest

from testcontainers.meilisearch import MeilisearchContainer


@pytest.mark.parametrize('version', ['latest', 'v1.2', 'v0.30'])
def test_run_meilisearch(version):
    with MeilisearchContainer(f'getmeili/meilisearch:{version}') as meilisearch_container:
        with urllib.request.urlopen(meilisearch_container.get_url() + '/health') as response:
            assert json.loads(response.read().decode())['status'] == 'available'


def test_run_meilisearch_with_master_key():
    with MeilisearchContainer('getmeili/meilisearch:latest', master_key='MASTER_KEY') as meilisearch_container:
        url = meilisearch_container.get_url() + '/version'
        master_key = meilisearch_container.get_master_key()
        request = urllib.request.Request(url, headers={'Authorization': f'Bearer {master_key}'})
        with urllib.request.urlopen(request) as response:
            assert 'pkgVersion' in json.loads(response.read().decode())
