from unittest.mock import MagicMock, patch

import docker

from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient


def test_docker_client_from_env():
    test_kwargs = {"test_kw": "test_value"}
    mock_docker = MagicMock(spec=docker)
    with patch("testcontainers.core.docker_client.docker", mock_docker):
        DockerClient(**test_kwargs)

    mock_docker.from_env.assert_called_with(**test_kwargs)


def test_container_docker_client_kw():
    test_kwargs = {"test_kw": "test_value"}
    mock_docker = MagicMock(spec=docker)
    with patch("testcontainers.core.docker_client.docker", mock_docker):
        DockerContainer(image="", docker_client_kw=test_kwargs)

    mock_docker.from_env.assert_called_with(**test_kwargs)
