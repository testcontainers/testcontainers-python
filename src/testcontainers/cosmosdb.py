import warnings

from testcontainers.community.cosmosdb import (
    CosmosDBMongoEndpointContainer,
    CosmosDBNoSQLEndpointContainer,
)

warnings.warn(
    "testcontainers.cosmosdb is deprecated, use testcontainers.community.cosmosdb instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "CosmosDBMongoEndpointContainer",
    "CosmosDBNoSQLEndpointContainer",
]
