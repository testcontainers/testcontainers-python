from time import sleep

from docker.models.containers import Container

from testcontainers.core.config import testcontainers_config
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.core.container import Reaper


def test_docker_container_reuse_default():
    with DockerContainer("hello-world") as container:
        assert container._reuse == False
        id = container._container.id
        wait_for_logs(container, "Hello from Docker!")
    containers = DockerClient().client.containers.list(all=True)
    assert id not in [container.id for container in containers]


def test_docker_container_with_reuse_reuse_disabled():
    with DockerContainer("hello-world").with_reuse() as container:
        assert container._reuse == True
        assert testcontainers_config.tc_properties_testcontainers_reuse_enable == False
        id = container._container.id
        wait_for_logs(container, "Hello from Docker!")
    containers = DockerClient().client.containers.list(all=True)
    assert id not in [container.id for container in containers]


def test_docker_container_with_reuse_reuse_enabled_ryuk_enabled(monkeypatch):
    # Make sure Ryuk cleanup is not active from previous test runs
    Reaper.delete_instance()

    tc_properties_mock = testcontainers_config.tc_properties | {"testcontainers.reuse.enable": "true"}
    monkeypatch.setattr(testcontainers_config, "tc_properties", tc_properties_mock)
    monkeypatch.setattr(testcontainers_config, "ryuk_reconnection_timeout", "0.1s")

    container = DockerContainer("hello-world").with_reuse().start()
    id = container._container.id
    wait_for_logs(container, "Hello from Docker!")

    Reaper._socket.close()
    # Sleep until Ryuk reaps all dangling containers
    sleep(0.6)

    containers = DockerClient().client.containers.list(all=True)
    assert id not in [container.id for container in containers]

    # Cleanup Ryuk class fields after manual Ryuk shutdown
    Reaper.delete_instance()


def test_docker_container_with_reuse_reuse_enabled_ryuk_disabled(monkeypatch):
    # Make sure Ryuk cleanup is not active from previous test runs
    Reaper.delete_instance()

    tc_properties_mock = testcontainers_config.tc_properties | {"testcontainers.reuse.enable": "true"}
    monkeypatch.setattr(testcontainers_config, "tc_properties", tc_properties_mock)
    monkeypatch.setattr(testcontainers_config, "ryuk_disabled", True)

    container = DockerContainer("hello-world").with_reuse().start()
    id = container._container.id
    wait_for_logs(container, "Hello from Docker!")

    containers = DockerClient().client.containers.list(all=True)
    assert id in [container.id for container in containers]

    # Cleanup after keeping container alive (with_reuse)
    container.stop()


def test_docker_container_with_reuse_reuse_enabled_ryuk_disabled_same_id(monkeypatch):
    # Make sure Ryuk cleanup is not active from previous test runs
    Reaper.delete_instance()

    tc_properties_mock = testcontainers_config.tc_properties | {"testcontainers.reuse.enable": "true"}
    monkeypatch.setattr(testcontainers_config, "tc_properties", tc_properties_mock)
    monkeypatch.setattr(testcontainers_config, "ryuk_disabled", True)

    container_1 = DockerContainer("hello-world").with_reuse().start()
    id_1 = container_1._container.id
    container_2 = DockerContainer("hello-world").with_reuse().start()
    id_2 = container_2._container.id
    assert id_1 == id_2

    # Cleanup after keeping container alive (with_reuse)
    container_1.stop()
    # container_2.stop() is not needed since it is the same as container_1


def test_docker_container_labels_hash():
    expected_hash = "91fde3c09244e1d3ec6f18a225b9261396b9a1cb0f6365b39b9795782817c128"
    with DockerContainer("hello-world").with_reuse() as container:
        assert container._container.labels["hash"] == expected_hash


def test_docker_client_find_container_by_hash_not_existing():
    with DockerContainer("hello-world"):
        assert DockerClient().find_container_by_hash("foo") == None


def test_docker_client_find_container_by_hash_existing():
    with DockerContainer("hello-world").with_reuse() as container:
        hash_ = container._container.labels["hash"]
        found_container = DockerClient().find_container_by_hash(hash_)
        assert isinstance(found_container, Container)
