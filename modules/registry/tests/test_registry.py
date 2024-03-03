from requests import Response, get
from requests.auth import HTTPBasicAuth
from testcontainers.registry import DockerRegistryContainer


REGISTRY_USERNAME: str = "foo"
REGISTRY_PASSWORD: str = "bar"


def test_registry():
    with DockerRegistryContainer().with_bind_ports(5000, 5000) as registry_container:
        url: str = f"http://{registry_container.get_registry()}/v2/_catalog"

        response: Response = get(url)

        assert response.status_code == 200


def test_registry_with_authentication():
    with DockerRegistryContainer(username=REGISTRY_USERNAME, password=REGISTRY_PASSWORD).with_bind_ports(
        5000, 5000
    ) as registry_container:
        url: str = f"http://{registry_container.get_registry()}/v2/_catalog"

        response: Response = get(url, auth=HTTPBasicAuth(REGISTRY_USERNAME, REGISTRY_PASSWORD))

        assert response.status_code == 200
