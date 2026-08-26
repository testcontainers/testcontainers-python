import warnings

from testcontainers.community.k3s import (
    K3SContainer,
)

warnings.warn(
    "testcontainers.k3s is deprecated, use testcontainers.community.k3s instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "K3SContainer",
]
