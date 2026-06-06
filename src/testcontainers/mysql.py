import warnings

from testcontainers.community.mysql import (
    MySqlContainer,
)

warnings.warn(
    "testcontainers.mysql is deprecated, use testcontainers.community.mysql instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "MySqlContainer",
]
