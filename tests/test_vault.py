import json
import urllib

import hvac
import pytest
from hvac.exceptions import InvalidRequest

from testcontainers.vault import VaultContainer


def test_docker_run_vault_unauthenticated():
    with VaultContainer('vault:1.5.3') as vault:
        resp = urllib.request.urlopen(vault.get_url() + '/v1/sys/health')
        assert json.loads(resp.read().decode())['version'] == '1.5.3'

        # client is not authenticated
        client = hvac.Client(url=vault.get_url())
        assert client.is_authenticated() is False
        assert client.sys.is_initialized()
        assert client.sys.is_sealed() is False

        # client cannot change the vault
        with pytest.raises(InvalidRequest):
            client.sys.enable_secrets_engine('transit')


def test_docker_run_vault_custom_token():
    with VaultContainer('vault:1.5.3').with_vault_token('my token') as vault:
        # login with custom token
        client = hvac.Client(url=vault.get_url(), token='my token')
        assert client.is_authenticated()
        assert client.sys.is_initialized()
        assert client.sys.is_sealed() is False

        # enable 'transit' engine and create a key
        client.sys.enable_secrets_engine('transit')
        client.secrets.transit.create_key(name='test-key', exportable=True)
        key = client.secrets.transit.export_key(name='test-key', key_type='hmac-key')
        assert key['data']['name'] == 'test-key'
        assert key['data']['keys']['1'] is not None
