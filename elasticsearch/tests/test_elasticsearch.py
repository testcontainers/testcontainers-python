import json
import urllib.request
import pytest

from testcontainers.elasticsearch import ElasticSearchContainer


# The versions below were the current supported versions at time of writing (2022-08-11)
@pytest.mark.parametrize('version', ['6.8.23', '7.17.5', '8.3.3'])
def test_docker_run_elasticsearch(version):
    # adding the mem_limit as per: https://stackoverflow.com/a/75701019
    # could also add (but not necessary): .with_env('discovery.type', 'single-node')
    with ElasticSearchContainer(f'elasticsearch:{version}', mem_limit='3G').with_env('discovery.type', 'single-node') as es:
        resp = urllib.request.urlopen(es.get_url())
        assert json.loads(resp.read().decode())['version']['number'] == version
