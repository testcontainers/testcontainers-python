import warnings

from testcontainers.community.registry import (
    DockerRegistryContainer,
)

warnings.warn(
    "testcontainers.registry is deprecated, use testcontainers.community.registry instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "DockerRegistryContainer",
]
