import warnings

from testcontainers.community.aws import (
    AWSLambdaContainer,
)

warnings.warn(
    "testcontainers.aws is deprecated, use testcontainers.community.aws instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "AWSLambdaContainer",
]
