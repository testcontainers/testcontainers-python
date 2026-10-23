from typing import Any, Optional, Union

import pytest
from docker.errors import APIError

from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import is_podman


@pytest.mark.parametrize(
    "container_port, host_port, expected_container_port",
    [
        ("8080", "8080", "8080/tcp"),
        ("8125/udp", "8125/udp", "8125/udp"),
        ("8092/udp", "8092/udp", "8092/udp"),
        ("9000/tcp", "9000/tcp", "9000/tcp"),
        ("8080", "8080/udp", "8080/udp"),
        (8080, 8080, "8080/tcp"),
        (9000, None, "9000/tcp"),
        ("9009", None, "9009/tcp"),
        ("9000", "", "9000/tcp"),
        ("9000/udp", "", "9000/udp"),
    ],
)
def test_docker_container_with_bind_ports(
    container_port: Union[str, int], host_port: Optional[Union[str, int]], expected_container_port: str
):
    container = DockerContainer("alpine:latest")
    container.with_bind_ports(container_port, host_port)
    container.start()

    # prepare to inspect container
    c_c = container._container
    assert c_c
    container_id = c_c.id
    assert container_id is not None
    client = c_c.client
    assert client is not None

    # assemble expected output to compare to container API
    host_port = str(host_port or "")
    expected = {expected_container_port: [{"HostIp": "", "HostPort": host_port.partition("/")[0]}]}

    # compare PortBindings to expected output
    actual = client.containers.get(container_id).attrs["HostConfig"]["PortBindings"]
    if is_podman():
        # Normalize Podman differences:
        # - HostIp '0.0.0.0' vs '' (both mean all interfaces)
        # - Empty host_port: Podman stores the assigned port, Docker stores ''
        for bindings in actual.values():
            for binding in bindings:
                if binding.get("HostIp") == "0.0.0.0":
                    binding["HostIp"] = ""
                if not host_port and binding.get("HostPort", "").isdigit():
                    binding["HostPort"] = ""
    assert actual == expected
    container.stop()


@pytest.mark.parametrize(
    "container_port, host_port",
    [
        ("0", "8080"),
        ("8080", "abc"),
        (0, 0),
        (-1, 8080),
        (None, 8080),
        ("8080/tcp", "8080/udp"),
    ],
)
def test_error_docker_container_with_bind_ports(container_port: Union[str, int], host_port: Optional[Union[str, int]]):
    with pytest.raises(APIError):
        container = DockerContainer("alpine:latest")
        container.with_bind_ports(container_port, host_port)
        container.start()


@pytest.mark.parametrize(
    "ports, expected",
    [
        (("8125/udp",), {"8125/udp": {}}),
        (("8092/udp", "9000/tcp"), {"8092/udp": {}, "9000/tcp": {}}),
        (("8080", "8080/udp"), {"8080/tcp": {}, "8080/udp": {}}),
        ((9000,), {"9000/tcp": {}}),
        ((8080, 8080), {"8080/tcp": {}}),
        (("9001", 9002), {"9001/tcp": {}, "9002/tcp": {}}),
        (("9001", 9002, "9003/udp", 9004), {"9001/tcp": {}, "9002/tcp": {}, "9003/udp": {}, "9004/tcp": {}}),
    ],
)
def test_docker_container_with_exposed_ports(ports: tuple[Union[str, int], ...], expected: dict[str, Any]):
    container = DockerContainer("alpine:latest")
    container.with_exposed_ports(*ports)
    container.start()

    c_c = container._container
    assert c_c
    container_id = c_c.id
    assert container_id is not None
    client = c_c.client
    assert client is not None
    assert client.containers.get(container_id).attrs["Config"]["ExposedPorts"] == expected
    container.stop()


@pytest.mark.parametrize(
    "ports",
    [
        ((9000, None)),
        (("", 9000)),
        ("tcp", ""),
    ],
)
def test_error_docker_container_with_exposed_ports(ports: tuple[Union[str, int], ...]):
    with pytest.raises(APIError):
        container = DockerContainer("alpine:latest")
        container.with_exposed_ports(*ports)
        container.start()
