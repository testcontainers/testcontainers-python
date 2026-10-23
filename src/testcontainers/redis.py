import warnings

from testcontainers.community.redis import (
    AsyncRedisContainer,
    PingWaitStrategy,
    RedisContainer,
)

warnings.warn(
    "testcontainers.redis is deprecated, use testcontainers.community.redis instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "AsyncRedisContainer",
    "PingWaitStrategy",
    "RedisContainer",
]
