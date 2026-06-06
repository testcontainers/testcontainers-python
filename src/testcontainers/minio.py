import warnings

from testcontainers.community.minio import (
    MinioContainer,
)

warnings.warn(
    "testcontainers.minio is deprecated, use testcontainers.community.minio instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "MinioContainer",
]
