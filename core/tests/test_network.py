from http import HTTPStatus
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.network import Network

import docker.errors
import pytest

NGINX_ALPINE_SLIM_IMAGE = "nginx:1.25.4-alpine-slim"


def test_network_gets_created_and_cleaned_up():
    with Network() as network:
        docker = DockerClient()
        networks_list = docker.client.networks.list(network.name)
        assert networks_list[0].name == network.name
        assert networks_list[0].id == network.id
    assert not docker.client.networks.list(network.name)


def test_network_create_wo_cm():
    network = Network()
    network.create()
    docker = DockerClient()
    networks_list = docker.client.networks.list(network.name)
    assert networks_list[0].name == network.name
    assert networks_list[0].id == network.id

    network.remove()
    assert not docker.client.networks.list(network.name)


def test_network_create_errors():
    network = Network()
    network.create()

    # calling create the second time should raise an error
    with pytest.raises(docker.errors.APIError) as excinfo:
        network.create()

    assert excinfo.value.response.status_code == HTTPStatus.CONFLICT
    excinfo.match(f"network with name {network.name} already exists")
    network.remove()


def test_containers_can_communicate_over_network():
    with Network() as network:
        with (
            DockerContainer(NGINX_ALPINE_SLIM_IMAGE)
            .with_name("alpine1")
            .with_network_aliases("alpine1-alias-1", "alpine1-alias-2")
            .with_network(network) as alpine1
        ):
            with (
                DockerContainer(NGINX_ALPINE_SLIM_IMAGE)
                .with_name("alpine2")
                .with_network_aliases("alpine2-alias-1", "alpine2-alias-2")
                .with_network(network) as alpine2
            ):
                assert_can_ping(alpine1, "alpine2")
                assert_can_ping(alpine1, "alpine2-alias-1")
                assert_can_ping(alpine1, "alpine2-alias-2")

                assert_can_ping(alpine2, "alpine1")
                assert_can_ping(alpine2, "alpine1-alias-1")
                assert_can_ping(alpine2, "alpine1-alias-2")


def assert_can_ping(container: DockerContainer, remote_name: str):
    status, output = container.exec("ping -c 1 %s" % remote_name)
    assert status == 0
    assert "64 bytes" in str(output)
