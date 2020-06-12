import pytest

from testcontainers.compose import DockerCompose
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.exceptions import NoSuchPortExposed


def test_can_spawn_service_via_compose():
    with DockerCompose("tests") as compose:
        host = compose.get_service_host("hub", 4444)
        port = compose.get_service_port("hub", 4444)
        assert host == "0.0.0.0"
        assert port == "4444"


def test_can_pull_images_before_spawning_service_via_compose():
    with DockerCompose("tests", pull=True) as compose:
        host = compose.get_service_host("hub", 4444)
        port = compose.get_service_port("hub", 4444)
        assert host == "0.0.0.0"
        assert port == "4444"


def test_can_throw_exception_if_no_port_exposed():
    with DockerCompose("tests") as compose:
        with pytest.raises(NoSuchPortExposed):
            compose.get_service_host("hub", 5555)


def test_compose_wait_for_container_ready():
    with DockerCompose("tests") as compose:
        docker = DockerClient()
        compose.wait_for("http://%s:4444/wd/hub" % docker.host())


def test_can_parse_multiple_compose_files():
    with DockerCompose(filepath="tests",
                       compose_file_name=["docker-compose.yml", "docker-compose-2.yml"]) as compose:
        host = compose.get_service_host("mysql", 3306)
        port = compose.get_service_port("mysql", 3306)
        assert host == "0.0.0.0"
        assert port == "3306"

        host = compose.get_service_host("hub", 4444)
        port = compose.get_service_port("hub", 4444)
        assert host == "0.0.0.0"
        assert port == "3306"
