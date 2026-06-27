import warnings

from testcontainers.community.selenium import (
    BrowserWebDriverContainer,
    SeleniumVideoContainer,
    get_image_name,
)

warnings.warn(
    "testcontainers.selenium is deprecated, use testcontainers.community.selenium instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "BrowserWebDriverContainer",
    "SeleniumVideoContainer",
    "get_image_name",
]
