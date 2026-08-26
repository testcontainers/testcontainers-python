import warnings

from testcontainers.community.db2 import (
    Db2Container,
)

warnings.warn(
    "testcontainers.db2 is deprecated, use testcontainers.community.db2 instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "Db2Container",
]
