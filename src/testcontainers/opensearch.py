import warnings

from testcontainers.community.opensearch import (
    OpenSearchContainer,
)

warnings.warn(
    "testcontainers.opensearch is deprecated, use testcontainers.community.opensearch instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "OpenSearchContainer",
]
