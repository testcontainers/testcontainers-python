import warnings

from testcontainers.community.mssql import (
    SqlServerContainer,
)

warnings.warn(
    "testcontainers.mssql is deprecated, use testcontainers.community.mssql instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "SqlServerContainer",
]
