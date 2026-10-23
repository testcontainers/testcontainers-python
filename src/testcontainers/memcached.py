import warnings

from testcontainers.community.memcached import (
    MemcachedContainer,
    MemcachedNotReady,
)

warnings.warn(
    "testcontainers.memcached is deprecated, use testcontainers.community.memcached instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "MemcachedContainer",
    "MemcachedNotReady",
]
