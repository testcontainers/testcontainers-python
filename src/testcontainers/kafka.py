import warnings

from testcontainers.community.kafka import (
    KafkaContainer,
    RedpandaContainer,
    kafka_config,
)

warnings.warn(
    "testcontainers.kafka is deprecated, use testcontainers.community.kafka instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "KafkaContainer",
    "RedpandaContainer",
    "kafka_config",
]
