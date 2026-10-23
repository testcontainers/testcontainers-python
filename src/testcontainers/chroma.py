import warnings

from testcontainers.community.chroma import (
    ChromaContainer,
)

warnings.warn(
    "testcontainers.chroma is deprecated, use testcontainers.community.chroma instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ChromaContainer",
]
