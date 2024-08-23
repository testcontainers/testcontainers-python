import pytest

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


def test_wait_for_logs() -> None:
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")


def test_timeout_is_raised_when_waiting_for_logs() -> None:
    with pytest.raises(TimeoutError), DockerContainer("alpine").with_command("sleep 2") as container:
        wait_for_logs(container, "Hello from Docker!", timeout=1e-3)
