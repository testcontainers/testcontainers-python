import os

import pytest

from testcontainers.compose import DockerCompose
from testcontainers.core.exceptions import NoSuchPortExposed


def test_can_spawn_service_via_compose():
    compose = DockerCompose(os.path.dirname(__file__))

    try:
        compose.start()
        host = compose.get_service_host("hub", 4444)
        port = compose.get_service_port("hub", 4444)
        assert host == "0.0.0.0"
        assert port == "4444"
    finally:
        compose.stop()


def test_can_throw_exception_if_no_port_exposed():
    compose = DockerCompose(os.path.dirname(__file__))

    compose.start()
    with pytest.raises(NoSuchPortExposed):
        compose.get_service_host("hub", 5555)

    compose.stop()


def test_compose_wait_for_container_ready():
    compose = DockerCompose(os.path.dirname(__file__))
    with compose:
        compose.wait_for("http://localhost:4444/wd/hub")
