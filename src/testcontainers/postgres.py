import warnings

from testcontainers.community.postgres import (
    PostgresContainer,
)

warnings.warn(
    "testcontainers.postgres is deprecated, use testcontainers.community.postgres instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "PostgresContainer",
]
