import requests

from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.socat.socat import SocatContainer


def test_socat_with_helloworld():
    with (
        Network() as network,
        DockerContainer("testcontainers/helloworld:1.2.0")
        .with_exposed_ports(8080)
        .with_network(network)
        .with_network_aliases("helloworld"),
        SocatContainer().with_network(network).with_target(8080, "helloworld") as socat,
    ):
        socat_url = f"http://{socat.get_container_host_ip()}:{socat.get_exposed_port(8080)}"

        response = requests.get(f"{socat_url}/ping")  # noqa: S113

        assert response.status_code == 200
        assert response.content == b"PONG"
