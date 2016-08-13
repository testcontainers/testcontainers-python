from testcontainers_python.docker_manager import DockerManager


def test_docker_manager():
    docker = DockerManager()
    hub = docker.run('selenium/hub', ports=[4444], port_bindings={4444: 4444}, name='selenium-hub')
    ff = docker.run('selenium/node-firefox:2.53.0', links={'selenium-hub': 'hub'})
    print(docker.get_containers())
    host_info = docker.get_host_info(hub)
    print(host_info)
    docker.remove(hub)
    docker.remove(ff)


def test_docker_images():
    docker = DockerManager()
    images = docker.images()
    for im in images:
        print(im)


def test_docker_image_exists():
    docker = DockerManager()
    assert docker.image_exists("selenium/node-chrome:latest")


def test_docker_pull():
    name = "selenium/hub:2.53.0"
    docker = DockerManager()
    if docker.image_exists(name):
        docker.remove_image(name, True)
    stream = docker.pull("selenium/hub")
    for line in stream:
        print(line)
