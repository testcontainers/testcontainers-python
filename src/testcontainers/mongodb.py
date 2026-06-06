import warnings

from testcontainers.community.mongodb import (
    MongoDBAtlasLocalContainer,
    MongoDbContainer,
)

warnings.warn(
    "testcontainers.mongodb is deprecated, use testcontainers.community.mongodb instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "MongoDBAtlasLocalContainer",
    "MongoDbContainer",
]
