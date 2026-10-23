import warnings

from testcontainers.community.mqtt import (
    MosquittoContainer,
)

warnings.warn(
    "testcontainers.mqtt is deprecated, use testcontainers.community.mqtt instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "MosquittoContainer",
]
