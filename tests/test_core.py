import pytest

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


def test_raise_timeout():
    with pytest.raises(TimeoutError):
        with DockerContainer("alpine").with_command("sleep 2") as container:
            wait_for_logs(container, "Hello from Docker!", timeout=1e-3)


def test_wait_for_hello():
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")


def test_can_get_logs():
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")
        stdout, stderr = container.get_logs()
        assert stdout, 'There should be something on stdout'
