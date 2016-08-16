from testcontainers_python.context_manager import docker_client
from testcontainers_python.docker_client import DockerClient


def test_docker_run_selenium():
    docker = DockerClient()
    docker.stop_all()
    docker.run('selenium/hub:2.53.0', bind_ports={4444: 4444}, name='selenium-hub')
    docker.run('selenium/node-firefox:2.53.0', links={'selenium-hub': 'hub'})
    containers = docker.get_containers()
    assert len(containers) >= 2
    docker.stop_all()
    assert len(docker.get_containers()) == 0


def test_docker_run_mysql():
    docker = DockerClient()
    mysql = docker.run('mysql:latest', bind_ports={3306: 3306}, env={"MYSQL_ROOT_PASSWORD": 123456})
    docker.stop(mysql)


def test_docker_images():
    docker = DockerClient()
    img = docker._cli.containers(all=True, filters={"name": "selenium-hub"})
    assert len(img) >= 0


def test_docker_image_exists():
    docker = DockerClient()
    docker.pull_image("selenium/node-chrome:latest")
    assert docker.image_exists("selenium/node-chrome:latest")


def test_docker_get_containers():
    docker = DockerClient()
    print docker.get_containers()


def test_docker_pull():
    name = "selenium/hub:2.53.0"
    docker = DockerClient()
    if docker.image_exists(name):
        docker.remove_image(name, True)
    docker.pull_image(name)
    assert docker.image_exists(name)


def test_docker_rm():
    docker = DockerClient()
    docker.run(image='selenium/hub:2.53.0', bind_ports={4444: 4444}, name='selenium-hub')
    docker.stop_all()


def test_docker_ctx_manager():
    with docker_client() as d:
        container = d.run('selenium/hub:2.53.0', {4444: 4444})
        print(container)
