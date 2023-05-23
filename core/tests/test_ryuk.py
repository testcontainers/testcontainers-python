from testcontainers.core.reaper import Reaper
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


def test_wait_for_reaper():
    container = DockerContainer("hello-world").start()
    wait_for_logs(container, "Hello from Docker!")

    assert Reaper._socket is not None
    Reaper._socket.close()

    assert Reaper._container is not None
    wait_for_logs(Reaper._container, r".* Removed 1 .*", timeout=15)

    Reaper.delete_instance()


def test_container_without_ryuk():
    with DockerContainer("hello-world").with_auto_remove(False) as container:
        wait_for_logs(container, "Hello from Docker!")
        assert Reaper._instance is None
