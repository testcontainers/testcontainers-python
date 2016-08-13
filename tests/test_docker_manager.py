from testcontainers_python.docker_manager import DockerManager


def test_docker_run_selenium():
    docker = DockerManager()
    docker.stop_all()
    hub = docker.run('selenium/hub:2.53.0', bind_ports={4444: 4444}, name='selenium-hub')
    ff = docker.run('selenium/node-firefox:2.53.0', links={'selenium-hub': 'hub'})
    print(docker.get_containers())
    containers = docker.get_containers()
    assert len(containers) >= 2
    for index, cont in enumerate(containers):
        print(index, cont)
    docker.remove(hub)
    docker.remove(ff)
    assert len(docker.get_containers()) == 0


def test_docker_run_mysql():
    docker = DockerManager()
    mysql = docker.run('mysql:latest', bind_ports={3306: 3306}, env={"MYSQL_ROOT_PASSWORD": 123456})
    docker.stop(mysql)


def test_docker_images():
    docker = DockerManager()
    images = docker.images()
    for im in images:
        print(im)


def test_docker_image_exists():
    docker = DockerManager()
    assert docker.image_exists("selenium/node-chrome:latest")


def test_docker_get_containers():
    docker = DockerManager()
    print docker.get_containers()


def test_docker_pull():
    name = "selenium/hub:2.53.0"
    docker = DockerManager()
    if docker.image_exists(name):
        docker.remove_image(name, True)
    stream = docker.pull(name)
    print list(stream)[-1]
