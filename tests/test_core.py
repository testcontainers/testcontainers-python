import pytest

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs, wait_for_port


def test_raise_timeout():
    with pytest.raises(TimeoutError):
        with DockerContainer("alpine").with_command("sleep 2") as container:
            wait_for_logs(container, "Hello from Docker!", timeout=1e-3)


def test_wait_for_hello():
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")


def test_raise_timeout_port():
    with pytest.raises(TimeoutError):
        with DockerContainer("alpine").with_command("nc -l -p 81").with_exposed_ports(80) as container:
            wait_for_port(container, 80, timeout=1)


def test_wait_for_port():
    with DockerContainer("alpine").with_command("nc -l -p 80").with_exposed_ports(80) as container:
        wait_for_port(container, 80)


def test_wait_for_port_custom_cmd():
    with DockerContainer("alpine").with_command("nc -l -p 80").with_exposed_ports(80) as container:
        wait_for_port(container, 80, cmd="nc -vz -w 1 localhost %d" % 80)
