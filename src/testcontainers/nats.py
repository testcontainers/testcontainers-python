import warnings

from testcontainers.community.nats import (
    NatsContainer,
)

warnings.warn(
    "testcontainers.nats is deprecated, use testcontainers.community.nats instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "NatsContainer",
]
