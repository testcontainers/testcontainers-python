from contextlib import contextmanager

import pytest

from testcontainers.core import container
from testcontainers.core.container import Reaper
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


@pytest.mark.skip("invalid test - ryuk logs 'Removed' right before exiting")
def test_wait_for_reaper():
    container = DockerContainer("hello-world").start()
    wait_for_logs(container, "Hello from Docker!")

    assert Reaper._socket is not None
    Reaper._socket.close()

    assert Reaper._container is not None
    wait_for_logs(Reaper._container, r".* Removed \d .*", timeout=30)

    Reaper.delete_instance()


@contextmanager
def reset_reaper_instance():
    old_value = Reaper._instance
    Reaper._instance = None
    yield
    Reaper._instance = old_value


def test_container_without_ryuk(monkeypatch):
    monkeypatch.setattr(container, "RYUK_DISABLED", True)
    with reset_reaper_instance(), DockerContainer("hello-world") as cont:
        wait_for_logs(cont, "Hello from Docker!")
        assert Reaper._instance is None
