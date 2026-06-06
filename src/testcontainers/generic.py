import warnings

from testcontainers.community.generic import (
    ServerContainer,
    SqlContainer,
)

warnings.warn(
    "testcontainers.generic is deprecated, use testcontainers.community.generic instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ServerContainer",
    "SqlContainer",
]
