from typing import TYPE_CHECKING, Optional

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
            >>> with DockerImage(tag="new_image", path=".") as image:
            ...    logs = image.get_logs()

    :param tag: Tag of the image
    :param path: Path to the Dockerfile
    """

    def __init__(
        self,
        tag: str,
        path: str,
        docker_client_kw: Optional[dict] = None,
        **kwargs,
    ) -> None:
        self.tag = tag
        self.path = path
        self._docker = DockerClient(**(docker_client_kw or {}))
        self._kwargs = kwargs

    def build(self, **kwargs) -> Self:
        logger.info(f"Building image {self.tag} from {self.path}")
        docker_client = self.get_docker_client()
        self._image, self._logs = docker_client.build(path=self.path, tag=self.tag, **kwargs)
        logger.info(f"Built image {self.tag}")
        return self

    def remove(self, force=True, noprune=False) -> None:
        """
        Remove the image.

        :param force: Remove the image even if it is in use
        :param noprune: Do not delete untagged parent images
        """
        if self._image:
            self._image.remove(force=force, noprune=noprune)
        self.get_docker_client().client.close()

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
