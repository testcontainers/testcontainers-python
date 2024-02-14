from pathlib import Path
from time import sleep

import pytest

from testcontainers.compose import DockerCompose, ContainerIsNotRunning

FIXTURES = Path(__file__).parent.joinpath('compose_fixtures')


def test_compose_no_file_name():
    basic = DockerCompose(context=FIXTURES / 'basic')
    assert basic.compose_file_name is None


def test_compose_str_file_name():
    basic = DockerCompose(context=FIXTURES / 'basic',
                          compose_file_name='docker-compose.yaml')
    assert basic.compose_file_name == ['docker-compose.yaml']


def test_compose_list_file_name():
    basic = DockerCompose(context=FIXTURES / 'basic',
                          compose_file_name=['docker-compose.yaml'])
    assert basic.compose_file_name == ['docker-compose.yaml']


def test_compose_stop():
    basic = DockerCompose(context=FIXTURES / 'basic')
    basic.stop()


def test_compose_start_stop():
    basic = DockerCompose(context=FIXTURES / 'basic')
    basic.start()
    basic.stop()


def test_compose():
    basic = DockerCompose(context=FIXTURES / 'basic')
    try:
        basic.start()
        containers = basic.get_containers(include_all=True)
        assert len(containers) == 1
        containers = basic.get_containers()
        assert len(containers) == 1
        sleep(1)  # container produces some logs

        from_all = containers[0]
        assert from_all.State == "running"
        assert from_all.Service == "alpine"

        by_name = basic.get_container("alpine")

        assert by_name.Name == from_all.Name
        assert by_name.Service == from_all.Service
        assert by_name.State == from_all.State
        assert by_name.ID == from_all.ID

        assert by_name.ExitCode == 0

        basic.stop(down=False)

        with pytest.raises(ContainerIsNotRunning):
            assert basic.get_container('alpine') is None

        stopped = basic.get_container('alpine', include_all=True)
        assert stopped.State == "exited"
    finally:
        basic.stop()


def test_compose_ports():
    single = DockerCompose(context=FIXTURES / 'port_single')
    # todo continue
