from testcontainers.keycloak import KeycloakContainer


def test_docker_run_keycloak():
    with KeycloakContainer("quay.io/keycloak/keycloak:24.0.1") as keycloak_admin:
        keycloak_admin.get_client().users_count()
