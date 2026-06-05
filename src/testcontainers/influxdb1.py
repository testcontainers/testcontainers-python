import warnings

from testcontainers.community.influxdb1 import (
    InfluxDb1Container,
)

warnings.warn(
    "testcontainers.influxdb1 is deprecated, use testcontainers.community.influxdb1 instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "InfluxDb1Container",
]
