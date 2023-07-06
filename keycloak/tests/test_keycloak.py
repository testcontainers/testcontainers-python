import pytest

from testcontainers.keycloak import KeycloakContainer


@pytest.mark.parametrize("version", ["nightly", "latest", "legacy", "21.1.2", "21.0.2", "20.0.5", "19.0.3",
                                     "19.0.3-legacy", "18.0.2", "18.0.2-legacy", "17.0.1", "17.0.1-legacy", "16.1.1",
                                     "15.1.1", "14.0.0", "13.0.1", "12.0.4", "11.0.2", "10.0.2", "9.0.3", "8.0.2",
                                     "7.0.1", "6.0.1", "5.0.0"])
def test_docker_run_keycloak(version: str):
    with KeycloakContainer(f"quay.io/keycloak/keycloak:{version}") as kc:
        assert kc.get_client().users_count() > 0
