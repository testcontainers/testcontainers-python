import warnings

from testcontainers.community.keycloak import (
    KeycloakContainer,
)

warnings.warn(
    "testcontainers.keycloak is deprecated, use testcontainers.community.keycloak instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "KeycloakContainer",
]
