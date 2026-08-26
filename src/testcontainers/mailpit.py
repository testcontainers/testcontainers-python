import warnings

from testcontainers.community.mailpit import (
    MailpitContainer,
    MailpitUser,
)

warnings.warn(
    "testcontainers.mailpit is deprecated, use testcontainers.community.mailpit instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "MailpitContainer",
    "MailpitUser",
]
