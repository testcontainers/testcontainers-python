from os import PathLike
from typing import TYPE_CHECKING, Optional, Union

from typing_extensions import Self

from testcontainers.core.docker_client import DockerClient
from testcontainers.core.utils import setup_logger

if TYPE_CHECKING:
    from docker.models.containers import Image

logger = setup_logger(__name__)


class DockerImage:
    """
    Basic image object to build Docker images.

    .. doctest::

            >>> from testcontainers.core.image import DockerImage

            >>> with DockerImage(path="./core/tests/image_fixtures/sample/", tag="test-image") as image:
            ...    logs = image.get_logs()

    :param tag: Tag for the image to be built (default: None)
    :param path: Path to the build context
    :param dockerfile_path: Path to the Dockerfile within the build context path (default: Dockerfile)
    :param no_cache: Bypass build cache; CLI's --no-cache
    """

    def __init__(
        self,
        path: Union[str, PathLike],
        docker_client_kw: Optional[dict] = None,
        tag: Optional[str] = None,
        clean_up: bool = True,
        dockerfile_path: Union[str, PathLike] = "Dockerfile",
        no_cache: bool = False,
        **kwargs,
    ) -> None:
        self.tag = tag
        self.path = path
        self._docker = DockerClient(**(docker_client_kw or {}))
        self.clean_up = clean_up
        self._kwargs = kwargs
        self._image = None
        self._logs = None
        self._dockerfile_path = dockerfile_path
        self._no_cache = no_cache

    def build(self, **kwargs) -> Self:
        logger.info(f"Building image from {self.path}")
        docker_client = self.get_docker_client()
        self._image, self._logs = docker_client.build(
            path=str(self.path), tag=self.tag, dockerfile=self._dockerfile_path, nocache=self._no_cache, **kwargs
        )
        logger.info(f"Built image {self.short_id} with tag {self.tag}")
        return self

    @property
    def short_id(self) -> str:
        """
        The ID of the image truncated to 12 characters, without the ``sha256:`` prefix.
        """
        if self._image.id.startswith("sha256:"):
            return self._image.id.split(":")[1][:12]
        return self._image.id[:12]

    def remove(self, force=True, noprune=False) -> None:
        """
        Remove the image.

        :param force: Remove the image even if it is in use
        :param noprune: Do not delete untagged parent images
        """
        if self._image and self.clean_up:
            logger.info(f"Removing image {self.short_id}")
            self._image.remove(force=force, noprune=noprune)
        self.get_docker_client().client.close()

    def __str__(self) -> str:
        return f"{self.tag if self.tag else self.short_id}"

    def __enter__(self) -> Self:
        return self.build()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.remove()

    def get_wrapped_image(self) -> "Image":
        return self._image

    def get_docker_client(self) -> DockerClient:
        return self._docker

    def get_logs(self) -> list[dict]:
        return list(self._logs)
