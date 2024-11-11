from pathlib import Path

import pytest
from typing import Callable
import subprocess
from testcontainers.core.container import DockerClient
from pprint import pprint
import sys

PROJECT_DIR = Path(__file__).parent.parent.parent.resolve()


def pytest_configure(config: pytest.Config) -> None:
    """
    Add configuration for custom pytest markers.
    """
    config.addinivalue_line(
        "markers",
        "inside_docker_check: test used to validate DinD/DooD are working as expected",
    )


@pytest.fixture(scope="session")
def python_testcontainer_image() -> str:
    """Build an image with test containers python for DinD and DooD tests"""
    py_version = ".".join(map(str, sys.version_info[:2]))
    image_name = f"testcontainers-python:{py_version}"
    subprocess.run(
        [*("docker", "build"), *("--build-arg", f"PYTHON_VERSION={py_version}"), *("-t", image_name), "."],
        cwd=PROJECT_DIR,
        check=True,
    )
    return image_name


@pytest.fixture
def check_for_image() -> Callable[[str, bool], None]:
    """Warp the check_for_image function in a fixture"""

    def _check_for_image(image_short_id: str, cleaned: bool) -> None:
        """
        Validates if the image is present or not.

        :param image_short_id: The short id of the image
        :param cleaned: True if the image should not be present, False otherwise
        """
        client = DockerClient()
        images = client.client.images.list()
        found = any(image.short_id.endswith(image_short_id) for image in images)
        assert found is not cleaned, f'Image {image_short_id} was {"found" if cleaned else "not found"}'

    return _check_for_image


@pytest.fixture
def show_container_attributes() -> None:
    """Wrap the show_container_attributes function in a fixture"""

    def _show_container_attributes(container_id: str) -> None:
        """Print the attributes of a container"""
        client = DockerClient().client
        data = client.containers.get(container_id).attrs
        pprint(data)

    return _show_container_attributes
