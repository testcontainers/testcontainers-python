import pytest

from testcontainers.keycloak import KeycloakContainer

@pytest.mark.parametrize(["version"], [("16.1.1", )])
def test_docker_run_keycloak(version):
    with KeycloakContainer('jboss/keycloak:{}'.format(version)) as kc:
        kc.get_client().users_count()
