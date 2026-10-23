import warnings

from testcontainers.community.qdrant import (
    QdrantContainer,
)

warnings.warn(
    "testcontainers.qdrant is deprecated, use testcontainers.community.qdrant instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "QdrantContainer",
]
