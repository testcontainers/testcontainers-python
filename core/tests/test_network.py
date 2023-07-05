from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.network import Network


def test_network_gets_created_and_cleaned_up():
    with Network("test-network") as network:
        docker = DockerClient()
        networks_list = docker.client.networks.list("test-network")
        assert networks_list[0].name == "test-network"
        assert networks_list[0].id == network.id
    assert not docker.client.networks.list("test-network")


def test_containers_can_communicate_over_network():
    with Network("network") as network:
        with DockerContainer("nginx:alpine-slim").with_name(
                "alpine1").with_kwargs(network=network.name) as alpine1:
            with DockerContainer("nginx:alpine-slim").with_name(
                    "alpine2").with_kwargs(network=network.name) as alpine2:
                status, output = alpine1.exec("ping -c 1 alpine2")
                assert status == 0
                assert "64 bytes" in str(output)

                status, output = alpine2.exec("ping -c 1 alpine1")
                assert status == 0
                assert "64 bytes" in str(output)
