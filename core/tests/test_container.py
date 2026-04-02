from typing import Any

import pytest

from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.config import ConnectionMode

FAKE_ID = "ABC123"


class FakeContainer:
    def __init__(self) -> None:
        self.attrs: dict[str, Any] = {}

    @property
    def id(self) -> str:
        return FAKE_ID


@pytest.fixture
def container(monkeypatch: pytest.MonkeyPatch) -> DockerContainer:
    """
    Fake initialized container
    """
    client = DockerClient()
    container = DockerContainer("foobar")
    monkeypatch.setattr(container, "_docker", client)
    monkeypatch.setattr(container, "_container", FakeContainer())

    return container


@pytest.mark.parametrize("mode", ["docker_host", "gateway_ip", "bridge_ip"])
def test_get_container_host_ip(container: DockerContainer, monkeypatch: pytest.MonkeyPatch, mode: str) -> None:
    """
    Depending on the connection mode the correct function is executed to the host_ip
    """
    connection_mode = ConnectionMode(mode)

    def result_fake(result: str, require_container_id):
        def fake_for_mode(*container_id: str):
            if require_container_id:
                assert len(container_id) == 1
                assert container_id[0] == FAKE_ID
            else:
                assert len(container_id) == 0
            return result

        return fake_for_mode

    client = container._docker

    monkeypatch.setattr(client, "get_connection_mode", lambda: connection_mode)
    monkeypatch.setattr(client, "gateway_ip", result_fake("gateway_ip", True))
    monkeypatch.setattr(client, "bridge_ip", result_fake("bridge_ip", True))
    monkeypatch.setattr(client, "host", result_fake("docker_host", False))

    assert container.get_container_host_ip() == mode


@pytest.mark.parametrize("mode", [ConnectionMode.gateway_ip, ConnectionMode.docker_host])
def test_get_exposed_port_mapped(
    container: DockerContainer, monkeypatch: pytest.MonkeyPatch, mode: ConnectionMode
) -> None:
    def fake_mapped(container_id: str, port: int) -> int:
        assert container_id == FAKE_ID
        assert port == 8080
        return 45678

    client = container._docker
    monkeypatch.setattr(client, "port", fake_mapped)
    monkeypatch.setattr(client, "get_connection_mode", lambda: mode)

    assert container._get_exposed_port(8080) == 45678


def test_get_exposed_port_original(container: DockerContainer, monkeypatch: pytest.MonkeyPatch) -> None:
    client = container._docker
    monkeypatch.setattr(client, "get_connection_mode", lambda: ConnectionMode.bridge_ip)

    assert container._get_exposed_port(8080) == 8080


@pytest.mark.parametrize(
    "init_attr,init_value,class_attr,stored_value",
    [
        ("command", "ps", "_command", "ps"),
        ("env", {"e1": "v1"}, "env", {"e1": "v1"}),
        ("name", "foo-bar", "_name", "foo-bar"),
        ("ports", [22, 80], "ports", {22: None, 80: None}),
        (
            "volumes",
            [("/tmp", "/tmp2", "ro")],
            "volumes",
            {"/tmp": {"bind": "/tmp2", "mode": "ro"}},
        ),
    ],
)
def test_attribute(init_attr, init_value, class_attr, stored_value):
    """Test that the attributes set through the __init__ function are properly stored."""
    with DockerContainer("ubuntu", **{init_attr: init_value}) as container:
        assert getattr(container, class_attr) == stored_value


def test_container_info():
    """Test get_container_info functionality with a real container."""
    with DockerContainer("alpine:latest").with_command("sleep 30") as container:
        info = container.get_container_info()
        assert info is not None
        assert info.Id is not None
        assert info.Name is not None
        assert info.Image is not None

        assert info.State is not None
        assert info.State.Status == "running"
        assert info.State.Running is True
        assert info.State.Pid is not None

        assert info.Config is not None
        assert info.Config.Image is not None
        assert info.Config.Hostname is not None

        network_settings = info.get_network_settings()
        assert network_settings is not None
        assert network_settings.Networks is not None

        info2 = container.get_container_info()
        assert info is info2


def test_container_info_network_details():
    """Test network details in container info."""
    with DockerContainer("nginx:alpine") as container:
        info = container.get_container_info()
        assert info is not None

        network_settings = info.get_network_settings()
        assert network_settings is not None

        if network_settings.Networks:
            network_name, network = next(iter(network_settings.Networks.items()))
            assert network.IPAddress is not None
            assert network.Gateway is not None
            assert network.NetworkID is not None
