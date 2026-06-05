import warnings

from testcontainers.community.influxdb2 import (
    InfluxDb2Container,
)

warnings.warn(
    "testcontainers.influxdb2 is deprecated, use testcontainers.community.influxdb2 instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "InfluxDb2Container",
]
