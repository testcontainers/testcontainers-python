import os
import json
from collections import namedtuple
from unittest import mock
from unittest.mock import MagicMock, patch

import docker

from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.auth import parse_docker_auth_config
from testcontainers.core.image import DockerImage

from pytest import mark


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
