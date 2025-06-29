import pytest

from testcontainers.core.config import (
    TestcontainersConfiguration as TCC,
    TC_FILE,
    TestcontainersConfiguration,
    get_user_overwritten_connection_mode,
    ConnectionMode,
    get_docker_socket,
)

from pytest import MonkeyPatch, mark, LogCaptureFixture

import logging
import tempfile
from unittest.mock import Mock


def test_read_tc_properties(monkeypatch: MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmpdirname:
        file = f"{tmpdirname}/{TC_FILE}"
        with open(file, "w") as f:
            f.write("tc.host=some_value\n")

        monkeypatch.setattr("testcontainers.core.config.TC_GLOBAL", file)

        config = TCC()
        assert config.tc_properties == {"tc.host": "some_value"}


@mark.parametrize("docker_auth_config_env", ["key=value", ""])
@mark.parametrize("warning_dict", [{}, {"key": "value"}, {"DOCKER_AUTH_CONFIG": "TEST"}])
@mark.parametrize("warning_dict_post", [{}, {"key": "value"}, {"DOCKER_AUTH_CONFIG": "TEST"}])
def test_docker_auth_config(
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
    docker_auth_config_env: str,
    warning_dict: dict[str, str],
    warning_dict_post: dict[str, str],
) -> None:
    monkeypatch.setattr("testcontainers.core.config._WARNINGS", warning_dict)
    monkeypatch.setenv("DOCKER_AUTH_CONFIG", docker_auth_config_env)
    caplog.set_level(logging.WARNING)

    config = TCC()
    if not docker_auth_config_env:
        assert config.docker_auth_config == ""
        assert caplog.text == ""
    else:
        assert config.docker_auth_config == docker_auth_config_env

    if "DOCKER_AUTH_CONFIG" in warning_dict:
        assert warning_dict["DOCKER_AUTH_CONFIG"] in caplog.text

    if warning_dict == {}:
        monkeypatch.setattr("testcontainers.core.config._WARNINGS", warning_dict_post)

    config.docker_auth_config = "new_value"
    assert config.docker_auth_config == "new_value"


def test_tc_properties_get_tc_host() -> None:
    config = TCC()
    config.tc_properties = {"tc.host": "some_value"}
    assert config.tc_properties_get_tc_host() == "some_value"


def test_timeout() -> None:
    config = TCC()
    config.max_tries = 2
    config.sleep_time = 3
    assert config.timeout == 6


def test_invalid_connection_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TESTCONTAINERS_CONNECTION_MODE", "FOOBAR")
    with pytest.raises(ValueError, match="Error parsing TESTCONTAINERS_CONNECTION_MODE.*FOOBAR.*"):
        get_user_overwritten_connection_mode()


@pytest.mark.parametrize("mode, use_mapped", (("bridge_ip", False), ("gateway_ip", True), ("docker_host", True)))
def test_valid_connection_mode(monkeypatch: pytest.MonkeyPatch, mode: str, use_mapped: bool) -> None:
    monkeypatch.setenv("TESTCONTAINERS_CONNECTION_MODE", mode)
    assert get_user_overwritten_connection_mode().use_mapped_port is use_mapped
    assert TestcontainersConfiguration().connection_mode_override.use_mapped_port is use_mapped


def test_no_connection_mode_given(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TESTCONTAINERS_CONNECTION_MODE", raising=False)
    assert get_user_overwritten_connection_mode() is None


def test_get_docker_socket_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    If TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE env var is given prefer it
    """
    monkeypatch.setenv("TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", "/var/test.socket")
    assert get_docker_socket() == "/var/test.socket"


@pytest.fixture
def mock_docker_client_connections(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Ensure the docker client does not make any actual network calls
    """
    from docker.transport.sshconn import SSHHTTPAdapter
    from docker.api.client import APIClient

    # ensure that no actual connection is tried
    monkeypatch.setattr(SSHHTTPAdapter, "_connect", Mock())
    monkeypatch.setattr(SSHHTTPAdapter, "_create_paramiko_client", Mock())
    monkeypatch.setattr(APIClient, "_retrieve_server_version", Mock(return_value="1.47"))


@pytest.mark.usefixtures("mock_docker_client_connections")
def test_get_docker_host_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    If non socket docker-host is given return default

    Still ryuk will properly still not work but this is the historical default

    """
    monkeypatch.delenv("TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", raising=False)
    # Define Fake SSH Docker client
    monkeypatch.setenv("DOCKER_HOST", "ssh://remote_host")
    assert get_docker_socket() == "/var/run/docker.sock"


@pytest.mark.usefixtures("mock_docker_client_connections")
def test_get_docker_host_non_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Use the socket determined by the Docker API Adapter
    """
    monkeypatch.delenv("TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", raising=False)
    # Define a Non-Root like Docker Client
    monkeypatch.setenv("DOCKER_HOST", "unix://var/run/user/1000/docker.sock")
    assert get_docker_socket() == "/var/run/user/1000/docker.sock"


@pytest.mark.usefixtures("mock_docker_client_connections")
def test_get_docker_host_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Use the socket determined by the Docker API Adapter
    """
    monkeypatch.delenv("TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", raising=False)
    # Define a Root like Docker Client
    monkeypatch.setenv("DOCKER_HOST", "unix://")
    assert get_docker_socket() == "/var/run/docker.sock"


def test_deprecated_settings() -> None:
    """
    Getting deprecated settings raises a DepcrationWarning
    """
    from testcontainers.core import config

    with pytest.warns(DeprecationWarning):
        assert config.TIMEOUT


def test_attribut_error() -> None:
    """
    Accessing a not existing attribute raises an AttributeError
    """
    from testcontainers.core import config

    with pytest.raises(AttributeError):
        config.missing
