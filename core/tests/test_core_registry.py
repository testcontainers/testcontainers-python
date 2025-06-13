"""Integration test using login to a private registry.

Note: Using the testcontainers-python library to test the Docker registry.
This could be considered a bad practice as it is not recommended to use the same library to test itself.
However, it is a very good use case for DockerRegistryContainer and allows us to test it thoroughly.
"""

import json
import os
import base64
import pytest

from docker.errors import NotFound

from testcontainers.core.config import testcontainers_config
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.waiting_utils import wait_for_logs

from testcontainers.registry import DockerRegistryContainer
from testcontainers.core.utils import is_mac


@pytest.mark.skipif(
    is_mac(),
    reason="Docker Desktop on macOS does not support insecure private registries without daemon reconfiguration",
)
def test_missing_on_private_registry(monkeypatch):
    username = "user"
    password = "pass"
    image = "hello-world"
    tag = "test"

    with DockerRegistryContainer(username=username, password=password) as registry:
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


@pytest.mark.skipif(
    is_mac(),
    reason="Docker Desktop on macOS does not support local insecure registries over HTTP without modifying daemon settings",
)
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

    with DockerRegistryContainer(username=username, password=password) as registry:
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
