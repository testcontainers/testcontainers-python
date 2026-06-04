import hvac
from testcontainers.vault import VaultContainer


def test_docker_run_vault():
    config = VaultContainer("hashicorp/vault:1.16.1")
    with config as vault:
        url = vault.get_connection_url()
        client = hvac.Client(url=url)
        status = client.sys.read_health_status()
        assert status.status_code == 200


def test_docker_run_vault_act_as_root():
    config = VaultContainer("hashicorp/vault:1.16.1")
    with config as vault:
        url = vault.get_connection_url()
        client = hvac.Client(url=url, token=vault.root_token)
        assert client.is_authenticated()
        assert client.sys.is_initialized()
        assert not client.sys.is_sealed()

        client.sys.enable_secrets_engine(
            backend_type="kv",
            path="secrets",
            config={
                "version": "2",
            },
        )
        client.secrets.kv.v2.create_or_update_secret(
            path="my-secret",
            mount_point="secrets",
            secret={
                "pssst": "this is secret",
            },
        )
        resp = client.secrets.kv.v2.read_secret(
            path="my-secret",
            mount_point="secrets",
        )
        assert resp["data"]["data"]["pssst"] == "this is secret"
