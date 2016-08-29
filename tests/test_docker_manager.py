#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os
from pprint import pprint

import MySQLdb

from testcontainers.core.docker_client import DockerClient
from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


# PostgresDockerContainer


def test_docker_run_selenium():
    docker = DockerClient()
    docker.stop_all()
    docker.run('selenium/hub:2.53.0', bind_ports={4444: 4444}, name='selenium-hub')
    docker.run('selenium/node-firefox:2.53.0', links={'selenium-hub': 'hub'})
    containers = docker.get_running_containers()
    assert len(containers) >= 2
    docker.stop_all()
    assert len(docker.get_running_containers()) == 0


def test_docker_images():
    docker = DockerClient()
    img = docker.containers(all=True, filters={"name": "selenium-hub"})
    assert len(img) >= 0


def test_docker_image_exists():
    docker = DockerClient()
    docker.pull_image("selenium/node-chrome:latest")
    assert docker.image_exists("selenium/node-chrome:latest")


def test_docker_get_containers():
    docker = DockerClient()
    print(docker.get_running_containers())


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


def test_generic_docker_container():
    container = DockerContainer(image_name="mariadb",
                                version="latest",
                                container_name="mariadb",
                                host_port=3306)
    container.add_env("MYSQL_ROOT_PASSWORD", "secret")
    container.add_env("MYSQL_DATABASE", "test_db")
    container.bind_ports(3306, 3306)
    with container as mariabd:
        @wait_container_is_ready()
        def connect():
            return MySQLdb.connect(host="0.0.0.0",
                                   user="root",
                                   passwd="secret",
                                   db="test_db")

        cur = connect().cursor()

        cur.execute("SELECT VERSION()")
        row = cur.fetchone()
        print("server version:", row[0])
        cur.close()
        assert row[0] == '10.1.16-MariaDB-1~jessie'
