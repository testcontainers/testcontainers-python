import warnings

from testcontainers.community.elasticsearch import (
    ElasticSearchContainer,
)

warnings.warn(
    "testcontainers.elasticsearch is deprecated, use testcontainers.community.elasticsearch instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ElasticSearchContainer",
]
