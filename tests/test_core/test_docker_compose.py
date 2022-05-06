from unittest.mock import patch

import pytest

from testcontainers.compose import DockerCompose
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.exceptions import NoSuchPortExposed
from testcontainers.core.waiting_utils import wait_for_logs


ROOT = "tests/test_core"


def test_can_spawn_service_via_compose():
    with DockerCompose(ROOT) as compose:
        host = compose.get_service_host("hub", 4444)
        port = compose.get_service_port("hub", 4444)
        assert host == "0.0.0.0"
        assert port == "4444"


def test_can_pull_images_before_spawning_service_via_compose():
    with DockerCompose(ROOT, pull=True) as compose:
        host = compose.get_service_host("hub", 4444)
        port = compose.get_service_port("hub", 4444)
        assert host == "0.0.0.0"
        assert port == "4444"


def test_can_build_images_before_spawning_service_via_compose():
    with patch.object(DockerCompose, "_call_command") as call_mock:
        with DockerCompose(ROOT, build=True) as compose:
            ...

    assert compose.build
    docker_compose_cmd = call_mock.call_args_list[0][1]["cmd"]
    assert "docker-compose" in docker_compose_cmd
    assert "up" in docker_compose_cmd
    assert "--build" in docker_compose_cmd


def test_can_throw_exception_if_no_port_exposed():
    with DockerCompose(ROOT) as compose:
        with pytest.raises(NoSuchPortExposed):
            compose.get_service_host("hub", 5555)


def test_compose_wait_for_container_ready():
    with DockerCompose(ROOT) as compose:
        docker = DockerClient()
        compose.wait_for("http://%s:4444/wd/hub" % docker.host())


def test_compose_can_wait_for_logs():
    with DockerCompose(filepath=ROOT, compose_file_name="docker-compose-4.yml") as compose:
        wait_for_logs(compose, "Hello from Docker!")


def test_can_parse_multiple_compose_files():
    with DockerCompose(filepath=ROOT,
                       compose_file_name=["docker-compose.yml", "docker-compose-2.yml"]) as compose:
        host = compose.get_service_host("alpine", 3306)
        port = compose.get_service_port("alpine", 3306)
        assert host == "0.0.0.0"
        assert port == "3306"

        host = compose.get_service_host("hub", 4444)
        port = compose.get_service_port("hub", 4444)
        assert host == "0.0.0.0"
        assert port == "4444"


def test_can_get_logs():
    with DockerCompose(ROOT) as compose:
        docker = DockerClient()
        compose.wait_for("http://%s:4444/wd/hub" % docker.host())
        stdout, stderr = compose.get_logs()
        assert stdout, 'There should be something on stdout'


def test_can_pass_env_params_by_env_file():
    with DockerCompose(ROOT, compose_file_name='docker-compose-3.yml',
                       env_file='.env.test') as compose:
        stdout, *_ = compose.exec_in_container("alpine", ["printenv"])
        assert stdout.splitlines()[0], 'test_has_passed'


def test_can_exec_commands():
    with DockerCompose(ROOT) as compose:
        result = compose.exec_in_container('hub', ['echo', 'my_test'])
        assert result[0] == 'my_test\n', "The echo should be successful"
        assert result[1] == '', "stderr should be empty"
        assert result[2] == 0, 'The exit code should be successful'
