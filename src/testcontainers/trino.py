import warnings

from testcontainers.community.trino import (
    TrinoContainer,
)

warnings.warn(
    "testcontainers.trino is deprecated, use testcontainers.community.trino instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "TrinoContainer",
]
