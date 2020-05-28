import pytest

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs, wait_for_port, wait_for_http_code


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


def test_wait_for_http_code():
    with DockerContainer("nginx").with_exposed_ports(80) as container:
        wait_for_http_code(container, 200)


def test_raise_timeout_for_http_code():
    with pytest.raises(TimeoutError):
        with DockerContainer("nginx").with_exposed_ports(81) as container:
            wait_for_http_code(container, 200, port=81, timeout=2)


def test_raise_timeout_invalid_path():
    with pytest.raises(TimeoutError):
        with DockerContainer("nginx").with_exposed_ports(80) as container:
            wait_for_http_code(container, 200, path="/fail", port=80, timeout=2)
