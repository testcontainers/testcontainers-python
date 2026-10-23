import warnings

from testcontainers.community.valkey import (
    ValkeyContainer,
)

warnings.warn(
    "testcontainers.valkey is deprecated, use testcontainers.community.valkey instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ValkeyContainer",
]
