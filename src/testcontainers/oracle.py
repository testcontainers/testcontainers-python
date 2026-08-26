import warnings

from testcontainers.community.oracle import (
    OracleDbContainer,
)

warnings.warn(
    "testcontainers.oracle is deprecated, use testcontainers.community.oracle instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "OracleDbContainer",
]
