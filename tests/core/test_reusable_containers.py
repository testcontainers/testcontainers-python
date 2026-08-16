from time import sleep

from docker.models.containers import Container

from testcontainers.core.config import testcontainers_config
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.core.container import Reaper


def test_docker_container_reuse_default():
    # Make sure Ryuk cleanup is not active from previous test runs
    Reaper.delete_instance()

    container = DockerContainer("hello-world").start()
    wait_for_logs(container, "Hello from Docker!")

    assert container._reuse == False
    assert testcontainers_config.tc_properties_testcontainers_reuse_enable() == False
    assert Reaper._socket is not None

    container.stop()
    containers = DockerClient().client.containers.list(all=True)
    assert container._container is not None
    assert container._container.id not in [container.id for container in containers]


def test_docker_container_with_reuse_reuse_disabled(caplog):
    # Make sure Ryuk cleanup is not active from previous test runs
    Reaper.delete_instance()

    container = DockerContainer("hello-world").with_reuse().start()
    wait_for_logs(container, "Hello from Docker!")

    assert container._reuse == True
    assert testcontainers_config.tc_properties_testcontainers_reuse_enable() == False
    assert ("Reuse was requested (`with_reuse`) but the environment does not support the ") in caplog.text
    assert Reaper._socket is not None

    container.stop()
    containers = DockerClient().client.containers.list(all=True)
    assert container._container is not None
    assert container._container.id not in [container.id for container in containers]


def test_docker_container_without_reuse_reuse_enabled(monkeypatch):
    # Make sure Ryuk cleanup is not active from previous test runs
    Reaper.delete_instance()

    tc_properties_mock = testcontainers_config.tc_properties | {"testcontainers.reuse.enable": "true"}
    monkeypatch.setattr(testcontainers_config, "tc_properties", tc_properties_mock)

    container = DockerContainer("hello-world").start()
    wait_for_logs(container, "Hello from Docker!")

    assert container._reuse == False
    assert testcontainers_config.tc_properties_testcontainers_reuse_enable() == True
    assert Reaper._socket is not None

    container.stop()
    containers = DockerClient().client.containers.list(all=True)
    assert container._container is not None
    assert container._container.id not in [container.id for container in containers]


def test_docker_container_with_reuse_reuse_enabled(monkeypatch):
    # Make sure Ryuk cleanup is not active from previous test runs
    Reaper.delete_instance()

    tc_properties_mock = testcontainers_config.tc_properties | {"testcontainers.reuse.enable": "true"}
    monkeypatch.setattr(testcontainers_config, "tc_properties", tc_properties_mock)

    container = DockerContainer("hello-world").with_reuse().start()
    wait_for_logs(container, "Hello from Docker!")

    assert Reaper._socket is None

    containers = DockerClient().client.containers.list(all=True)
    assert container._container is not None
    assert container._container.id in [container.id for container in containers]

    # Cleanup after keeping container alive (with_reuse)
    container.stop()


def test_docker_container_with_reuse_reuse_enabled_same_id(monkeypatch):
    # Make sure Ryuk cleanup is not active from previous test runs
    Reaper.delete_instance()

    tc_properties_mock = testcontainers_config.tc_properties | {"testcontainers.reuse.enable": "true"}
    monkeypatch.setattr(testcontainers_config, "tc_properties", tc_properties_mock)

    container_1 = DockerContainer("hello-world").with_reuse().start()
    assert container_1._container is not None
    id_1 = container_1._container.id
    container_2 = DockerContainer("hello-world").with_reuse().start()
    assert container_2._container is not None
    id_2 = container_2._container.id
    assert Reaper._socket is None
    assert id_1 == id_2
    # Cleanup after keeping container alive (with_reuse)
    container_1.stop()
    # container_2.stop() is not needed since it is the same as container_1


def test_docker_container_labels_hash_default():
    # w/out reuse
    with DockerContainer("hello-world") as container:
        assert container._container is not None
        assert "hash" not in container._container.labels.keys()


def test_docker_container_labels_hash(monkeypatch):
    tc_properties_mock = testcontainers_config.tc_properties | {"testcontainers.reuse.enable": "true"}
    monkeypatch.setattr(testcontainers_config, "tc_properties", tc_properties_mock)
    expected_hash = "380705419"
    with DockerContainer("hello-world").with_reuse() as container:
        assert container._container is not None
        assert container._container.labels["hash"] == expected_hash


def test_docker_client_find_container_by_hash_not_existing():
    with DockerContainer("hello-world"):
        assert DockerClient().find_container_by_hash("foo") == None


def test_docker_client_find_container_by_hash_existing(monkeypatch):
    tc_properties_mock = testcontainers_config.tc_properties | {"testcontainers.reuse.enable": "true"}
    monkeypatch.setattr(testcontainers_config, "tc_properties", tc_properties_mock)
    with DockerContainer("hello-world").with_reuse() as container:
        assert container._container is not None
        hash_ = container._container.labels["hash"]
        found_container = DockerClient().find_container_by_hash(hash_)
        assert isinstance(found_container, Container)
