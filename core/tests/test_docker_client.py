import os
from collections import namedtuple
from unittest import mock
from unittest.mock import MagicMock, patch

import docker

from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.utils import parse_docker_auth_config


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
    TestAuth = namedtuple("Auth", "value")
    mock_parse_docker_auth_config.return_value = [TestAuth("test")]

    with (
        mock.patch.object(c, "_docker_auth_config", "test"),
        patch("testcontainers.core.docker_client.docker", mock_docker),
        patch("testcontainers.core.docker_client.parse_docker_auth_config", mock_parse_docker_auth_config),
    ):
        DockerClient()

    mock_docker.from_env.return_value.login.assert_called_with(**{"value": "test"})


def test_container_docker_client_kw():
    test_kwargs = {"test_kw": "test_value"}
    mock_docker = MagicMock(spec=docker)
    with patch("testcontainers.core.docker_client.docker", mock_docker):
        DockerContainer(image="", docker_client_kw=test_kwargs)

    mock_docker.from_env.assert_called_with(**test_kwargs)
