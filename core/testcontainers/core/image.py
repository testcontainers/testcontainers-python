import functools as ft
from typing import Optional

import docker
from docker.client import DockerClient
from docker.models.images import Image, ImageCollection

from .utils import setup_logger

LOGGER = setup_logger(__name__)


class DockerImage:
    """
    Basic class to manage docker images.

    .. doctest::
            >>> from testcontainers.core.image import DockerImage

            >>> image = DockerImage().from_dockerfile(path="core/tests/", tag="testcontainers/test-image")
            >>> image.exists("testcontainers/test-image")
            True
            >>> image.get("testcontainers/test-image").id
            'sha256:...'
            >>> image.remove(force=True)
            >>> image.exists("testcontainers/test-image")
            False
    """

    def __init__(self, docker_client_kw: Optional[dict] = None, **kwargs) -> None:
        self._docker = DockerClient().from_env(**(docker_client_kw or {}))

    def from_dockerfile(self, path: str, tag: str = "local/image") -> "DockerImage":
        """
        Build an image from a Dockerfile.

        Args:
            path (str): Path to the Dockerfile
            tag (str): Tag for the image

        Returns:
            DockerImage: The current instance
        """
        self.build(path=path, tag=tag)
        return self

    def from_image(self, repository: str, tag: str = "latest") -> "DockerImage":
        """
        Pull an image from the registry.

        Args:
            repository (str): Image repository
            tag (str): Image tag

        Returns:
            DockerImage: The current instance
        """
        self.pull(repository=repository, tag=tag)
        return self

    @ft.wraps(ImageCollection.build)
    def build(self, **kwargs) -> "DockerImage":
        LOGGER.info("Building image from Dockerfile")
        self._image, _ = self._docker.images.build(**kwargs)
        return self

    @ft.wraps(ImageCollection.pull)
    def pull(self, **kwargs) -> Image:
        LOGGER.info("Pulling image")
        self._image = self._docker.images.pull(**kwargs)
        return self

    @ft.wraps(ImageCollection.get)
    def get(self, image: str) -> Image:
        LOGGER.info(f"Getting image {image}")
        image_obj = self._docker.images.get(image)
        return image_obj

    @ft.wraps(ImageCollection.remove)
    def remove(self, **kwargs) -> None:
        LOGGER.info(f"Removing image {self._image}")
        self._image.remove(**kwargs)

    @property
    def id(self) -> str:
        return self._image.id

    @property
    def short_id(self) -> str:
        return self._image.short_id

    @property
    def tags(self) -> dict:
        return self._image.tags

    def get_wrapped_image(self) -> Image:
        return self._image

    def exists(self, image: str) -> bool:
        """
        Check if the image exists in the local registry.

        Args:
            image (str): Image name

        Returns:
            bool: True if the image exists, False otherwise
        Raises:
            docker.errors.ImageNotFound: If the image does not exist
        """
        try:
            self.get(image)
            return True
        except docker.errors.ImageNotFound:
            return False
