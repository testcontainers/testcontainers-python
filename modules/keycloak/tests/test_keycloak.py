import pytest
from testcontainers.keycloak import KeycloakContainer


@pytest.mark.parametrize("image_version", ["26.4.0", "26.0.0", "25.0", "24.0.1", "18.0"])
def test_docker_run_keycloak(image_version: str):
    with KeycloakContainer(f"quay.io/keycloak/keycloak:{image_version}") as keycloak_admin:
        assert keycloak_admin.get_client().users_count() == 1


def test_docker_run_keycloak_with_management_relative_path():
    with KeycloakContainer("quay.io/keycloak/keycloak:26.4.0").with_env(
        "KC_HTTP_MANAGEMENT_RELATIVE_PATH", "/some/deeply/nested/path"
    ) as keycloak_admin:
        assert keycloak_admin.get_client().users_count() == 1
