import warnings

from testcontainers.community.nginx import (
    NginxContainer,
)

warnings.warn(
    "testcontainers.nginx is deprecated, use testcontainers.community.nginx instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "NginxContainer",
]
