import os
from pprint import pprint

from testcontainers.core.docker_client import DockerClient


def test_docker_run():
    docker = DockerClient()
    docker.stop_all()
    docker.run('selenium/hub:2.53.0', bind_ports={4444: 4444}, name='selenium-hub')
    docker.run('selenium/node-firefox:2.53.0', links={'selenium-hub': 'hub'})
    containers = docker.get_running_containers()
    assert len(containers) >= 2
    docker.stop_all()
    assert len(docker.get_running_containers()) == 0


def test_docker_pull():
    name = "selenium/hub:2.53.0"
    docker = DockerClient()
    if docker.image_exists(name):
        docker.remove_image(name, True)
    docker.pull_image(name)
    assert docker.image_exists(name)


def test_docker_image_exists():
    docker = DockerClient()
    docker.pull_image("selenium/node-chrome:latest")
    assert docker.image_exists("selenium/node-chrome:latest")


def test_docker_stop_all():
    docker = DockerClient()
    docker.run(image='selenium/hub:2.53.0', bind_ports={4444: 4444}, name='selenium-hub')
    docker.stop_all()


def test_docker_get_containers():
    docker = DockerClient()
    img = docker.get_containers(all=True, filters={"name": "selenium-hub"})
    assert len(img) >= 0


def test_docker_get_running_containers():
    docker = DockerClient()
    print(docker.get_running_containers())


def test_docker_build():
    dockerfile = """
                FROM busybox:buildroot-2014.02
                MAINTAINER first last, first.last@yourdomain.com
                VOLUME /data
                CMD ["/bin/sh"]
                """

    docker = DockerClient()
    docker.build(dockerfile=dockerfile, tag="my_container")
    out = docker.images("my_container")
    pprint(out)
    assert len(out) == 1
    assert out[0]['RepoTags'][0] == 'my_container:latest'


def test_docker_build_with_dockerfile():
    docker = DockerClient()

    dockerfile = open(os.path.dirname(os.path.realpath(__file__)) +
                      "/Dockerfile").read()

    docker.build(dockerfile=dockerfile, tag="my_container_2")
    out = docker.images("my_container_2")
    pprint(out)
    assert len(out) == 1
    assert out[0]['RepoTags'][0] == 'my_container_2:latest'


def test_docker_build_from_path():
    docker = DockerClient()
    docker.build_from_path(os.path.dirname(os.path.realpath(__file__)), tag="video_service")
