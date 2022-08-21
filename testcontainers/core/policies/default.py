from docker.models.images import Image

from testcontainers.core.policies.base import ImagePullPolicy


class DefaultPullPolicy(ImagePullPolicy):
    """The default ImagePullPolicy, which pulls the image from a remote repository only if it does not exist locally"""

    def should_pull_cached(self, image: Image) -> bool:
        return super().should_pull_cached(image)
