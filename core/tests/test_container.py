from typing import Any

import pytest

from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient, ContainerInspectInfo
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


def test_get_container_info_returns_none_when_no_container(
    container: DockerContainer, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test get_container_info returns None when container is not started."""
    monkeypatch.setattr(container, "_container", None)
    info = container.get_container_info()
    assert info is None


def test_get_container_info_lazy_loading(container: DockerContainer, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test get_container_info lazy loading and caching."""
    fake_data = {"Id": "test123", "Name": "/test-container", "Image": "nginx:alpine"}
    fake_info = ContainerInspectInfo.from_dict(fake_data)

    monkeypatch.setattr(container._docker, "get_container_inspect_info", lambda _: fake_info)

    info1 = container.get_container_info()
    assert info1 is not None
    assert info1.Id == "test123"
    assert info1.Name == "/test-container"
    assert info1.Image == "nginx:alpine"

    info2 = container.get_container_info()
    assert info1 is info2


def test_get_container_info_structure(container: DockerContainer, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test get_container_info returns properly structured data."""
    fake_data = {
        "Id": "abc123def456",
        "Name": "/my-test-container",
        "Image": "sha256:nginx123",
        "Created": "2023-01-01T00:00:00Z",
        "State": {
            "Status": "running",
            "Running": True,
            "Pid": 5678,
            "ExitCode": 0,
            "Health": {"Status": "healthy", "FailingStreak": 0, "Log": [{"Output": "healthy"}]},
        },
        "Config": {
            "Image": "nginx:alpine",
            "Hostname": "my-hostname",
            "Env": ["PATH=/usr/bin", "HOME=/root"],
            "Cmd": ["nginx", "-g", "daemon off;"],
            "ExposedPorts": {"80/tcp": {}},
        },
        "NetworkSettings": {
            "IPAddress": "172.17.0.3",
            "Gateway": "172.17.0.1",
            "Networks": {
                "bridge": {
                    "IPAddress": "172.17.0.3",
                    "Gateway": "172.17.0.1",
                    "NetworkID": "net123",
                    "MacAddress": "02:42:ac:11:00:03",
                    "Aliases": ["container-alias"],
                }
            },
        },
        "HostConfig": {"Memory": 1073741824, "CpuShares": 1024, "NetworkMode": "bridge"},
    }
    fake_info = ContainerInspectInfo.from_dict(fake_data)

    monkeypatch.setattr(container._docker, "get_container_inspect_info", lambda _: fake_info)

    info = container.get_container_info()
    assert info is not None

    assert info.Id == "abc123def456"
    assert info.Name == "/my-test-container"
    assert info.Image == "sha256:nginx123"
    assert info.Created == "2023-01-01T00:00:00Z"

    assert info.State is not None
    assert info.State.Status == "running"
    assert info.State.Running is True
    assert info.State.Pid == 5678
    assert info.State.ExitCode == 0
    assert info.State.Health is not None
    assert info.State.Health.Status == "healthy"
    assert info.State.Health.FailingStreak == 0
    assert info.State.Health.Log is not None
    assert len(info.State.Health.Log) == 1
    assert info.State.Health.Log[0].Output == "healthy"

    assert info.Config is not None
    assert info.Config.Image == "nginx:alpine"
    assert info.Config.Hostname == "my-hostname"
    assert info.Config.Env == ["PATH=/usr/bin", "HOME=/root"]
    assert info.Config.Cmd == ["nginx", "-g", "daemon off;"]
    assert info.Config.ExposedPorts == {"80/tcp": {}}

    network_settings = info.get_network_settings()
    assert network_settings is not None
    assert network_settings.IPAddress == "172.17.0.3"
    assert network_settings.Gateway == "172.17.0.1"

    assert network_settings.Networks is not None
    assert "bridge" in network_settings.Networks
    bridge_network = network_settings.Networks["bridge"]
    assert bridge_network.IPAddress == "172.17.0.3"
    assert bridge_network.Gateway == "172.17.0.1"
    assert bridge_network.NetworkID == "net123"
    assert bridge_network.MacAddress == "02:42:ac:11:00:03"
    assert bridge_network.Aliases == ["container-alias"]

    assert info.HostConfig is not None
    assert info.HostConfig.Memory == 1073741824
    assert info.HostConfig.CpuShares == 1024
    assert info.HostConfig.NetworkMode == "bridge"


def test_get_container_info_handles_exceptions(container: DockerContainer, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test get_container_info handles exceptions gracefully."""

    def mock_exception(_):
        raise Exception("Docker API error")

    monkeypatch.setattr(container._docker, "get_container_inspect_info", mock_exception)

    info = container.get_container_info()
    assert info is None


def test_get_container_info_with_none_values(container: DockerContainer, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test get_container_info handles None values in HostConfig and NetworkSettings."""
    fake_data = {
        "Id": "test-none-values",
        "Name": "/test-none",
        "Image": "nginx:alpine",
        "NetworkSettings": {"IPAddress": "172.17.0.2", "Networks": None, "Ports": None},
        "HostConfig": {"Memory": 0, "NetworkMode": "bridge", "PortBindings": None},
    }
    fake_info = ContainerInspectInfo.from_dict(fake_data)

    monkeypatch.setattr(container._docker, "get_container_inspect_info", lambda _: fake_info)

    info = container.get_container_info()
    assert info is not None
    assert info.Id == "test-none-values"

    network_settings = info.get_network_settings()
    assert network_settings is not None
    assert network_settings.IPAddress == "172.17.0.2"
    assert network_settings.Networks is None
    assert network_settings.Ports is None

    assert info.HostConfig is not None
    assert info.HostConfig.Memory == 0
    assert info.HostConfig.NetworkMode == "bridge"
    assert info.HostConfig.PortBindings is None


def test_get_container_info_with_port_bindings(container: DockerContainer, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test get_container_info handles port bindings correctly."""
    fake_data = {
        "Id": "test-port-bindings",
        "Name": "/test-ports",
        "Image": "nginx:alpine",
        "NetworkSettings": {"Ports": {"80/tcp": [{"HostPort": "8080"}], "443/tcp": None}},
        "HostConfig": {"NetworkMode": "bridge", "PortBindings": {"80/tcp": [{"HostPort": "8080"}], "443/tcp": None}},
    }
    fake_info = ContainerInspectInfo.from_dict(fake_data)

    monkeypatch.setattr(container._docker, "get_container_inspect_info", lambda _: fake_info)

    info = container.get_container_info()
    assert info is not None

    network_settings = info.get_network_settings()
    assert network_settings is not None
    assert network_settings.Ports is not None
    assert "80/tcp" in network_settings.Ports
    port_bindings = network_settings.Ports["80/tcp"]
    assert port_bindings is not None
    assert len(port_bindings) == 1
    assert port_bindings[0].HostPort == "8080"
    assert network_settings.Ports["443/tcp"] is None

    assert info.HostConfig is not None
    assert info.HostConfig.PortBindings is not None
    assert "80/tcp" in info.HostConfig.PortBindings
    host_port_bindings = info.HostConfig.PortBindings["80/tcp"]
    assert host_port_bindings is not None
    assert len(host_port_bindings) == 1
    assert host_port_bindings[0].HostPort == "8080"
    assert info.HostConfig.PortBindings["443/tcp"] is None


def test_get_container_info_edge_cases_regression(container: DockerContainer, monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression test for None value handling."""
    fake_data = {
        "Id": "regression-test",
        "Name": "/regression-container",
        "Image": "nginx:alpine",
        "NetworkSettings": {"IPAddress": "172.17.0.2", "Networks": None, "Ports": None},
        "HostConfig": {"Memory": 0, "NetworkMode": "bridge", "PortBindings": None},
    }
    fake_info = ContainerInspectInfo.from_dict(fake_data)

    monkeypatch.setattr(container._docker, "get_container_inspect_info", lambda _: fake_info)

    info = container.get_container_info()
    assert info is not None
    assert info.Id == "regression-test"

    network_settings = info.get_network_settings()
    assert network_settings is not None
    assert network_settings.Networks is None
    assert network_settings.Ports is None

    host_config = info.HostConfig
    assert host_config is not None
    assert host_config.PortBindings is None
