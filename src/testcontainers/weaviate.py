import warnings

from testcontainers.community.weaviate import (
    WeaviateContainer,
)

warnings.warn(
    "testcontainers.weaviate is deprecated, use testcontainers.community.weaviate instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "WeaviateContainer",
]
