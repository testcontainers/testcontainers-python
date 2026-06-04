import pytest
from typing import Callable
from testcontainers.core.container import DockerClient


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
        assert found is not cleaned, f"Image {image_short_id} was {'found' if cleaned else 'not found'}"

    return _check_for_image
