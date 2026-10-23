import warnings

from testcontainers.community.scylla import (
    ScyllaContainer,
)

warnings.warn(
    "testcontainers.scylla is deprecated, use testcontainers.community.scylla instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ScyllaContainer",
]
