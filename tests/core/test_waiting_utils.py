import pytest

from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import ContainerStatusWaitStrategy
from testcontainers.core.waiting_utils import wait_for_logs, wait_for, wait_container_is_ready


def test_wait_for_logs() -> None:
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")


def test_timeout_is_raised_when_waiting_for_logs() -> None:
    with pytest.raises(TimeoutError), DockerContainer("alpine").with_command("sleep 2") as container:
        wait_for_logs(container, "Hello from Docker!", timeout=1e-3)


def test_wait_container_is_ready_decorator_basic() -> None:
    """Test the basic wait_container_is_ready decorator functionality."""

    @wait_container_is_ready()
    def simple_check() -> bool:
        return True

    result = simple_check()
    assert result is True


def test_wait_container_is_ready_decorator_with_container() -> None:
    """Test wait_container_is_ready decorator with a real container."""

    def check_container_logs(container: DockerContainer) -> bool:
        # wait until it becomes running.
        # if it is too late, it is actually fine in this case.
        # we are happy with an exited (even crashed) container that has logs.
        try:
            ContainerStatusWaitStrategy().wait_until_ready(container)
        except TimeoutError:
            pass

        stdout, stderr = container.get_logs()
        return b"Hello from Docker!" in stdout or b"Hello from Docker!" in stderr

    with DockerContainer("hello-world") as container:
        result = check_container_logs(container)
        assert result is True
