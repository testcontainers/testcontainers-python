import warnings

from testcontainers.community.vault import (
    VaultContainer,
)

warnings.warn(
    "testcontainers.vault is deprecated, use testcontainers.community.vault instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "VaultContainer",
]
