import warnings

from testcontainers.community.arangodb import (
    ArangoDbContainer,
)

warnings.warn(
    "testcontainers.arangodb is deprecated, use testcontainers.community.arangodb instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ArangoDbContainer",
]
