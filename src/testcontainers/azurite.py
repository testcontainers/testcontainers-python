import warnings

from testcontainers.community.azurite import (
    AzuriteContainer,
    ConnectionStringType,
)

warnings.warn(
    "testcontainers.azurite is deprecated, use testcontainers.community.azurite instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "AzuriteContainer",
    "ConnectionStringType",
]
