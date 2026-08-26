import warnings

from testcontainers.community.cockroachdb import (
    CockroachDBContainer,
)

warnings.warn(
    "testcontainers.cockroachdb is deprecated, use testcontainers.community.cockroachdb instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "CockroachDBContainer",
]
