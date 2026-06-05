import warnings

from testcontainers.community.cassandra import (
    CassandraContainer,
)

warnings.warn(
    "testcontainers.cassandra is deprecated, use testcontainers.community.cassandra instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "CassandraContainer",
]
