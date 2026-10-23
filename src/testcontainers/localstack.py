import warnings

from testcontainers.community.localstack import (
    LocalStackContainer,
)

warnings.warn(
    "testcontainers.localstack is deprecated, use testcontainers.community.localstack instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "LocalStackContainer",
]
