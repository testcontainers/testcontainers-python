import pytest

from testcontainers.compose import DockerCompose
from testcontainers.core.exceptions import NoSuchPortExposed
from testcontainers.core.utils import inside_container
from tests import TESTS_DIR


def test_can_spawn_service_via_compose():
    with DockerCompose(TESTS_DIR) as compose:
        host = compose.get_service_host("hub", 4444)
        port = compose.get_service_port("hub", 4444)
        assert host == "0.0.0.0"
        assert port == "4444"


def test_can_pull_images_before_spawning_service_via_compose():
    with DockerCompose(TESTS_DIR, pull=True) as compose:
        host = compose.get_service_host("hub", 4444)
        port = compose.get_service_port("hub", 4444)
        assert host == "0.0.0.0"
        assert port == "4444"


def test_can_throw_exception_if_no_port_exposed():
    with DockerCompose(TESTS_DIR) as compose:
        with pytest.raises(NoSuchPortExposed):
            compose.get_service_host("hub", 5555)


def test_compose_wait_for_container_ready():
    with DockerCompose(TESTS_DIR) as compose:
        host = "host.docker.internal" if inside_container() else "localhost"
        compose.wait_for("http://%s:4444/wd/hub" % host)
