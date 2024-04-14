from time import sleep
import pytest
from pytest import MonkeyPatch

from docker import DockerClient
from docker.errors import NotFound

from testcontainers.core.config import testcontainers_config
from testcontainers.core.container import Reaper
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


def test_wait_for_reaper(monkeypatch: MonkeyPatch):
    Reaper.delete_instance()
    monkeypatch.setattr(testcontainers_config, "ryuk_reconnection_timeout", "0.1s")
    docker_client = DockerClient()
    container = DockerContainer("hello-world").start()

    container_id = container.get_wrapped_container().short_id
    reaper_id = Reaper._container.get_wrapped_container().short_id

    assert docker_client.containers.get(container_id) is not None
    assert docker_client.containers.get(reaper_id) is not None

    wait_for_logs(container, "Hello from Docker!")

    Reaper._socket.close()

    sleep(0.6)  # Sleep until Ryuk reaps all dangling containers. 0.5 extra seconds for good measure.

    with pytest.raises(NotFound):
        docker_client.containers.get(container_id)
    with pytest.raises(NotFound):
        docker_client.containers.get(reaper_id)

    # Cleanup Ryuk class fields after manual Ryuk shutdown
    Reaper.delete_instance()


def test_container_without_ryuk(monkeypatch: MonkeyPatch):
    Reaper.delete_instance()
    monkeypatch.setattr(testcontainers_config, "ryuk_disabled", True)
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")
        assert Reaper._instance is None


def test_ryuk_is_reused_in_same_process():
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")
        reaper_instance = Reaper._instance

    assert reaper_instance is not None

    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")
        assert reaper_instance is Reaper._instance
