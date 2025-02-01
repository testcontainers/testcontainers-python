import pytest
from testcontainers.keycloak import KeycloakContainer


@pytest.mark.parametrize("image_version", ["latest", "26.0.0"])
def test_docker_run_keycloak(image_version: str):
    with KeycloakContainer(f"quay.io/keycloak/keycloak:{image_version}") as keycloak_admin:
        assert keycloak_admin.get_client().users_count() == 1
