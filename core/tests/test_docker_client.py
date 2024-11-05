import os
import json
from collections import namedtuple
from typing import Any
from unittest import mock
from unittest.mock import MagicMock, patch

import docker
import pytest

from testcontainers.core.config import testcontainers_config as c, ConnectionMode
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.auth import parse_docker_auth_config
from testcontainers.core.image import DockerImage
from testcontainers.core import utils

from pytest import mark

from docker.models.networks import Network


def test_docker_client_from_env():
    test_kwargs = {"test_kw": "test_value"}
    mock_docker = MagicMock(spec=docker)
    with patch("testcontainers.core.docker_client.docker", mock_docker):
        DockerClient(**test_kwargs)

    mock_docker.from_env.assert_called_with(**test_kwargs)


def test_docker_client_login_no_login():
    with patch.dict(os.environ, {}, clear=True):
        mock_docker = MagicMock(spec=docker)
        with patch("testcontainers.core.docker_client.docker", mock_docker):
            DockerClient()

        mock_docker.from_env.return_value.login.assert_not_called()


def test_docker_client_login():
    mock_docker = MagicMock(spec=docker)
    mock_parse_docker_auth_config = MagicMock(spec=parse_docker_auth_config)
    mock_utils = MagicMock()
    mock_utils.parse_docker_auth_config = mock_parse_docker_auth_config
    Auth = namedtuple("Auth", "value")
    mock_parse_docker_auth_config.return_value = [Auth("test")]

    with (
        mock.patch.object(c, "_docker_auth_config", "test"),
        patch("testcontainers.core.docker_client.docker", mock_docker),
        patch("testcontainers.core.docker_client.parse_docker_auth_config", mock_parse_docker_auth_config),
    ):
        DockerClient()

    mock_docker.from_env.return_value.login.assert_called_with(**{"value": "test"})


def test_docker_client_login_empty_get_docker_auth_config():
    mock_docker = MagicMock(spec=docker)
    mock_get_docker_auth_config = MagicMock()
    mock_get_docker_auth_config.return_value = None

    with (
        mock.patch.object(c, "_docker_auth_config", "test"),
        patch("testcontainers.core.docker_client.docker", mock_docker),
        patch("testcontainers.core.docker_client.get_docker_auth_config", mock_get_docker_auth_config),
    ):
        DockerClient()

    mock_docker.from_env.return_value.login.assert_not_called()


def test_docker_client_login_empty_parse_docker_auth_config():
    mock_docker = MagicMock(spec=docker)
    mock_parse_docker_auth_config = MagicMock(spec=parse_docker_auth_config)
    mock_utils = MagicMock()
    mock_utils.parse_docker_auth_config = mock_parse_docker_auth_config
    mock_parse_docker_auth_config.return_value = None

    with (
        mock.patch.object(c, "_docker_auth_config", "test"),
        patch("testcontainers.core.docker_client.docker", mock_docker),
        patch("testcontainers.core.docker_client.parse_docker_auth_config", mock_parse_docker_auth_config),
    ):
        DockerClient()

    mock_docker.from_env.return_value.login.assert_not_called()


# This is used to make sure we don't fail (nor try to login) when we have unsupported auth config
@mark.parametrize("auth_config_sample", [{"credHelpers": {"test": "login"}}, {"credsStore": "login"}])
def test_docker_client_login_unsupported_auth_config(auth_config_sample):
    mock_docker = MagicMock(spec=docker)
    mock_get_docker_auth_config = MagicMock()
    mock_get_docker_auth_config.return_value = json.dumps(auth_config_sample)

    with (
        mock.patch.object(c, "_docker_auth_config", "test"),
        patch("testcontainers.core.docker_client.docker", mock_docker),
        patch("testcontainers.core.docker_client.get_docker_auth_config", mock_get_docker_auth_config),
    ):
        DockerClient()

    mock_docker.from_env.return_value.login.assert_not_called()


def test_container_docker_client_kw():
    test_kwargs = {"test_kw": "test_value"}
    mock_docker = MagicMock(spec=docker)
    with patch("testcontainers.core.docker_client.docker", mock_docker):
        DockerContainer(image="", docker_client_kw=test_kwargs)

    mock_docker.from_env.assert_called_with(**test_kwargs)


def test_image_docker_client_kw():
    test_kwargs = {"test_kw": "test_value"}
    mock_docker = MagicMock(spec=docker)
    with patch("testcontainers.core.docker_client.docker", mock_docker):
        DockerImage(name="", path="", docker_client_kw=test_kwargs)

    mock_docker.from_env.assert_called_with(**test_kwargs)


def test_host_prefer_host_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(c, "tc_host_override", "my_docker_host")
    assert DockerClient().host() == "my_docker_host"


@pytest.mark.parametrize(
    "base_url, expected",
    [
        pytest.param("http://[-", "localhost", id="invalid_url"),
        pytest.param("http+docker://localhost", "localhost", id="docker_socket"),
        pytest.param("http://localnpipe", "localhost", id="docker_socket_windows"),
        pytest.param("http://some_host", "some_host", id="other_host"),
        pytest.param("unix://something", "1.2.3.4", id="inside_container_socket"),
    ],
)
def test_host(monkeypatch: pytest.MonkeyPatch, base_url: str, expected: str) -> None:
    client = DockerClient()
    monkeypatch.setattr(client.client.api, "base_url", base_url)
    monkeypatch.setattr(c, "tc_host_override", None)
    # overwrite some utils in order to test all branches of host
    monkeypatch.setattr(utils, "is_windows", lambda: True)
    monkeypatch.setattr(utils, "inside_container", lambda: True)
    monkeypatch.setattr(utils, "default_gateway_ip", lambda: "1.2.3.4")

    assert client.host() == expected


def test_get_connection_mode_overwritten(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(c, "connection_mode_override", ConnectionMode.gateway_ip)
    assert DockerClient().get_connection_mode() == ConnectionMode.gateway_ip


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "::1"])
def test_get_connection_mode_localhost_inside_container(monkeypatch: pytest.MonkeyPatch, host: str) -> None:
    """
    If docker host is localhost and we are inside a container prefer gateway_ip
    """
    client = DockerClient()
    monkeypatch.setattr(c, "connection_mode_override", None)
    monkeypatch.setattr(client, "host", lambda: host)
    monkeypatch.setattr(client, "find_host_network", lambda: None)
    monkeypatch.setattr(utils, "inside_container", lambda: True)
    assert client.get_connection_mode() == ConnectionMode.gateway_ip


def test_get_connection_mode_remote_docker_host(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Use docker_host inside container if remote docker host is given
    """
    client = DockerClient()
    monkeypatch.setattr(c, "connection_mode_override", None)
    monkeypatch.setattr(client, "host", lambda: "remote.docker.host")
    monkeypatch.setattr(client, "find_host_network", lambda: None)
    monkeypatch.setattr(utils, "inside_container", lambda: True)
    assert client.get_connection_mode() == ConnectionMode.docker_host


def test_get_connection_mode_dood(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    For docker out of docker (docker socket mount), we expect to be able
    to find a host network.

    In this case we should use the bridge ip as we can't expect
    that either docker_host nor gateway_ip of the container are actually
    reachable from within this network.

    This is the case for instance if using Gitlab CIs `FF_NETWORK_PER_BUILD` flag
    """
    client = DockerClient()
    monkeypatch.setattr(c, "connection_mode_override", None)
    monkeypatch.setattr(client, "host", lambda: "localhost")
    monkeypatch.setattr(client, "find_host_network", lambda: "new_bridge_network")
    monkeypatch.setattr(utils, "inside_container", lambda: True)
    assert client.get_connection_mode() == ConnectionMode.bridge_ip


def test_find_host_network_invalid_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    If the hostname can't be resolved just return None
    """
    client = DockerClient()
    monkeypatch.setattr(client, "host", lambda: "this does not exists")
    assert client.find_host_network() is None


def test_find_host_network_found_by_docker_host(monkeypatch: pytest.MonkeyPatch) -> None:
    client = DockerClient()
    monkeypatch.setattr(client, "host", lambda: "172.22.0.1")

    networks = [
        # a network without IPAM
        {"Name": "host"},
        # network with invalid subnet
        {
            "Name": "invalid",
            "IPAM": {"Config": [{"Gateway": "172.22.0.1", "Subnet": "invalid subnet"}]},
        },
        {
            "Attachable": False,
            "ConfigFrom": {"Network": ""},
            "ConfigOnly": False,
            "Containers": {},
            "Created": "2024-10-11T16:08:36.005642863Z",
            "Driver": "bridge",
            "EnableIPv6": False,
            "Name": "runner-346da30e-2641-1-8365005",
            "IPAM": {
                "Config": [{"Gateway": "172.22.0.1", "Subnet": "172.22.0.0/16"}],
                "Driver": "default",
                "Options": None,
            },
        },
    ]

    class FakeNetworks:
        def list(self, filters: dict[str, str]) -> list[Network]:
            assert filters == {"type": "custom"}
            return [Network(network) for network in networks]

    class FakeClient:
        @property
        def networks(self):
            return FakeNetworks()

    monkeypatch.setattr(client, "client", FakeClient())

    assert client.find_host_network() == "runner-346da30e-2641-1-8365005"


def test_find_host_network_found_by_running_id(monkeypatch: pytest.MonkeyPatch) -> None:
    client = DockerClient()
    fake_id = "abcde1234"

    def network_name(container_id: str) -> str:
        assert container_id == fake_id
        return "FAKE_NETWORK"

    monkeypatch.setattr(utils, "get_running_in_container_id", lambda: fake_id)
    monkeypatch.setattr(client, "network_name", network_name)

    assert client.find_host_network() == "FAKE_NETWORK"


def test_run_uses_found_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    If a host network is found, use it
    """

    client = DockerClient()

    class ContainerRunFake:
        def __init__(self) -> None:
            self.calls: list[dict[str, Any]] = []

        def run(self, image: str, **kwargs: Any) -> str:
            self.calls.append(kwargs)
            return "CONTAINER"

    class FakeClient:
        def __init__(self) -> None:
            self.containers = ContainerRunFake()

    fake_client = FakeClient()

    monkeypatch.setattr(client, "find_host_network", lambda: "new_bridge_network")
    monkeypatch.setattr(client, "client", fake_client)

    assert client.run("test") == "CONTAINER"

    assert fake_client.containers.calls[0]["network"] == "new_bridge_network"
