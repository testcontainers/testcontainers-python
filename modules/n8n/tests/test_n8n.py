import json
from urllib.request import Request, urlopen

from testcontainers.n8n import N8nContainer


def test_docker_run_n8n():
    with N8nContainer("docker.n8n.io/n8nio/n8n:latest") as n8n:
        url = n8n.get_url()
        with urlopen(f"{url}/healthz") as response:
            assert response.status == 200
            data = json.loads(response.read().decode())
            assert data["status"] == "ok"


def test_n8n_api_key():
    with N8nContainer() as n8n:
        api_key = n8n.get_api_key()
        assert api_key is not None
        req = Request(
            f"{n8n.get_url()}/api/v1/workflows",
            headers={"X-N8N-API-KEY": api_key},
        )
        with urlopen(req, timeout=10) as response:
            assert response.status == 200
            data = json.loads(response.read().decode())
            assert "data" in data


def test_n8n_get_webhook_url():
    with N8nContainer() as n8n:
        webhook_url = n8n.get_webhook_url()
        assert "/webhook-test" in webhook_url
