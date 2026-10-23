import warnings

from testcontainers.community.neo4j import (
    Neo4jContainer,
)

warnings.warn(
    "testcontainers.neo4j is deprecated, use testcontainers.community.neo4j instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "Neo4jContainer",
]
