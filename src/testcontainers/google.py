import warnings

from testcontainers.community.google import (
    DatastoreContainer,
    PubSubContainer,
)

warnings.warn(
    "testcontainers.google is deprecated, use testcontainers.community.google instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "DatastoreContainer",
    "PubSubContainer",
]
