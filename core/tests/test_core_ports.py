import pytest
from typing import Union, Optional
from testcontainers.core.container import DockerContainer

from docker.errors import APIError


@pytest.mark.parametrize(
    "container_port, host_port",
    [
        ("8080", "8080"),
        ("8125/udp", "8125/udp"),
        ("8092/udp", "8092/udp"),
        ("9000/tcp", "9000/tcp"),
        ("8080", "8080/udp"),
        (8080, 8080),
        (9000, None),
        ("9009", None),
        ("9000", ""),
        ("9000/udp", ""),
    ],
)
def test_docker_container_with_bind_ports(container_port: Union[str, int], host_port: Optional[Union[str, int]]):
    container = DockerContainer("alpine:latest")
    container.with_bind_ports(container_port, host_port)
    container.start()

    # prepare to inspect container
    container_id = container._container.id
    client = container._container.client

    # assemble expected output to compare to container API
    container_port = str(container_port)
    host_port = str(host_port or "")

    # if the port protocol is not specified, it will default to tcp
    if "/" not in container_port:
        container_port += "/tcp"

    expected = {container_port: [{"HostIp": "", "HostPort": host_port}]}

    # compare PortBindings to expected output
    assert client.containers.get(container_id).attrs["HostConfig"]["PortBindings"] == expected
    container.stop()


@pytest.mark.parametrize(
    "container_port, host_port",
    [
        ("0", "8080"),
        ("8080", "abc"),
        (0, 0),
        (-1, 8080),
        (None, 8080),
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
def test_docker_container_with_exposed_ports(ports: tuple[Union[str, int], ...], expected: dict):
    container = DockerContainer("alpine:latest")
    container.with_exposed_ports(*ports)
    container.start()

    container_id = container._container.id
    client = container._container.client
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
