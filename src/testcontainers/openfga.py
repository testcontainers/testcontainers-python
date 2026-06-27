import warnings

from testcontainers.community.openfga import (
    OpenFGAContainer,
)

warnings.warn(
    "testcontainers.openfga is deprecated, use testcontainers.community.openfga instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "OpenFGAContainer",
]
