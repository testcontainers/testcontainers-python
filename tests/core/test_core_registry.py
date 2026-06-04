"""
Integration tests for private-registry support in ``DockerClient``.

These tests spin up a real ``registry:2`` container and exercise the wiring that turns ``DOCKER_AUTH_CONFIG`` into a successful login + image pull.
The registry is provided by the local ``_LocalRegistryContainer`` helper, kept as a private copy in ``core/tests`` so ``core`` does not import from a sibling module.

Skipped where insecure HTTP registries cannot be reached without daemon reconfiguration.
That includes macOS, Podman, and SSH-based Docker hosts.
"""

import base64
import json

import pytest
from _local_registry_container import _LocalRegistryContainer  # type: ignore[import-not-found]
from docker.errors import NotFound

from testcontainers.core.config import testcontainers_config
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient, is_podman, is_ssh_docker_host
from testcontainers.core.utils import is_mac
from testcontainers.core.waiting_utils import wait_for_logs

_skip_insecure_registry = pytest.mark.skipif(
    is_mac() or is_podman() or is_ssh_docker_host(),
    reason="Insecure HTTP registries are not supported without daemon reconfiguration on macOS, Podman, or SSH-based Docker hosts",
)


@_skip_insecure_registry
def test_missing_on_private_registry(monkeypatch):
    username = "user"
    password = "pass"
    image = "hello-world"
    tag = "test"

    with _LocalRegistryContainer(username=username, password=password) as registry:
        registry_url = registry.get_registry()

        # prepare auth config
        creds: bytes = base64.b64encode(f"{username}:{password}".encode("utf-8"))
        config = {"auths": {f"{registry_url}": {"auth": creds.decode("utf-8")}}}
        monkeypatch.setattr(testcontainers_config, name="docker_auth_config", value=json.dumps(config))
        assert testcontainers_config.docker_auth_config, "docker_auth_config not set"

        with pytest.raises(NotFound):
            # Test a container with image from private registry
            with DockerContainer(f"{registry_url}/{image}:{tag}") as test_container:
                wait_for_logs(test_container, "Hello from Docker!")


@_skip_insecure_registry
@pytest.mark.parametrize(
    "image,tag,username,password,expected_output",
    [
        ("nginx", "test", "user", "pass", "start worker processes"),
        ("hello-world", "latest", "new_user", "new_pass", "Hello from Docker!"),
        ("alpine", "3.12", None, None, ""),
    ],
)
def test_with_private_registry(image, tag, username, password, expected_output, monkeypatch):
    client = DockerClient().client

    with _LocalRegistryContainer(username=username, password=password) as registry:
        registry_url = registry.get_registry()

        # prepare image
        _image = client.images.pull(image)
        assert _image.tag(repository=f"{registry_url}/{image}", tag=tag), "Image not tagged"

        # login to private registry
        client.login(registry=registry_url, username=username, password=password)

        # push image to private registry
        client.images.push(f"{registry_url}/{image}")

        # clear local image so we will pull from private registry
        client.images.remove(f"{registry_url}/{image}:{tag}")

        # prepare auth config
        creds: bytes = base64.b64encode(f"{username}:{password}".encode("utf-8"))
        config = {"auths": {f"{registry_url}": {"auth": creds.decode("utf-8")}}}
        monkeypatch.setattr(testcontainers_config, name="docker_auth_config", value=json.dumps(config))
        assert testcontainers_config.docker_auth_config, "docker_auth_config not set"

        # Test a container with image from private registry
        with DockerContainer(f"{registry_url}/{image}:{tag}") as test_container:
            wait_for_logs(test_container, expected_output)

    # cleanup
    client.images.remove(f"{registry_url}/{image}:{tag}")
    client.close()
