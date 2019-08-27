import os
from pathlib import Path

from testcontainers import mysql

from testcontainers.core.generic import GenericContainer
from testcontainers.core.container import DockerContainer

from importlib import reload


def setup_module(m):
    os.environ["MYSQL_USER"] = "demo"
    os.environ["MYSQL_DATABASE"] = "custom_db"


def test_docker_custom_image():
    container = GenericContainer("mysql:5.7.17")
    container.with_exposed_ports(3306)
    container.with_env("MYSQL_ROOT_PASSWORD", "root")

    with container:
        port = container.get_exposed_port(3306)
        assert int(port) > 0


def test_docker_env_variables():
    reload(mysql)

    db = mysql.MySqlContainer()
    db.with_bind_ports(3306, 32785)
    with db:
        url = db.get_connection_url()
        assert url == 'mysql+pymysql://demo:test@0.0.0.0:32785/custom_db'

def test_docker_parameters_using_kwargs():
    code_dir = Path(__file__).parent
    container_first = GenericContainer("nginx:latest")
    container_first.with_volume_mapping(code_dir, '/code')

    container_second = GenericContainer("nginx:latest", working_dir='/code')

    print(container_second._kwargs)
    with container_first:
        container_second.with_kwargs(volumes_from=[container_first._container.short_id])
        with container_second:
            files_first = container_first.exec('ls /code').output.decode('utf-8').strip()
            files_second = container_second.exec('ls /code').output.decode('utf-8').strip()
            assert files_first == files_second
            
            pwd_first = container_first.exec('pwd').output.decode('utf-8').strip()
            pwd_second = container_second.exec('pwd').output.decode('utf-8').strip()
            assert pwd_first != pwd_second
            assert pwd_second == '/code'

def test_container_environments():
    code_dir = Path(__file__).parent
    container = DockerContainer("nginx:latest")
    container.with_env('TEST', 'test')
    container.with_env('DOCKER', 'docker')

    with container:
        output = container.exec("bash -c 'echo $TEST $DOCKER'").output.decode('utf-8').strip()
        assert output == 'test docker'

def test_add_map_entry():
    code_dir = Path(__file__).parent
    container = DockerContainer("nginx:latest")
    container._with_map_entry('something', 'is', 'arbitary')
    container._with_map_entry('something', 'also', 'arbitary')

    assert container._kwargs['something'] == {'also': 'arbitary', 'is': 'arbitary'}

def test_add_map_entry_override_non_mapping_value():
    code_dir = Path(__file__).parent
    container = DockerContainer("nginx:latest", something='initial-value-is-not-a-map')
    container._with_map_entry('something', 'is', 'arbitrary')
    container._with_map_entry('something', 'also', 'arbitrary')
    container.with_bind_ports(8080, 80)
    container.with_exposed_ports(8000)
    container.with_env('test', 'value')
    container.with_volume_mapping(code_dir, '/code')

    assert container._kwargs['something'] == {'also': 'arbitary', 'is': 'arbitary'}
    assert container._kwargs['ports'] == {8000: None, 8080: 80}
    assert container._kwargs['environment'] == {'test': 'value'}
    assert container._kwargs['volumes'] == {code_dir: {'bind': '/code', 'mode': 'ro'}}
