import warnings

from testcontainers.community.sftp import (
    SFTPContainer,
    SFTPUser,
)

warnings.warn(
    "testcontainers.sftp is deprecated, use testcontainers.community.sftp instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "SFTPContainer",
    "SFTPUser",
]
