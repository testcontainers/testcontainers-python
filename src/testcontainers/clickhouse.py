import warnings

from testcontainers.community.clickhouse import (
    ClickHouseContainer,
)

warnings.warn(
    "testcontainers.clickhouse is deprecated, use testcontainers.community.clickhouse instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ClickHouseContainer",
]
