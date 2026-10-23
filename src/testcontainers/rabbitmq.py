import warnings

from testcontainers.community.rabbitmq import (
    RabbitMqContainer,
)

warnings.warn(
    "testcontainers.rabbitmq is deprecated, use testcontainers.community.rabbitmq instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "RabbitMqContainer",
]
