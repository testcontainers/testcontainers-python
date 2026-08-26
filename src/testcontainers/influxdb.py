import warnings

from testcontainers.community.influxdb import (
    InfluxDbContainer,
)

warnings.warn(
    "testcontainers.influxdb is deprecated, use testcontainers.community.influxdb instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "InfluxDbContainer",
]
