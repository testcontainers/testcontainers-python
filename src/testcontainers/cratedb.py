import warnings

from testcontainers.community.cratedb import (
    CrateDBContainer,
)

warnings.warn(
    "testcontainers.cratedb is deprecated, use testcontainers.community.cratedb instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "CrateDBContainer",
]
