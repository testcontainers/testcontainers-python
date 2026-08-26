import warnings

from testcontainers.community.milvus import (
    MilvusContainer,
)

warnings.warn(
    "testcontainers.milvus is deprecated, use testcontainers.community.milvus instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "MilvusContainer",
]
