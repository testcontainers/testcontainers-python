from testcontainers.docker_client import DockerClient
from testcontainers.generic import GenericDockerContainer
from testcontainers.mysql import MySqlDockerContainer


def test_docker_run_selenium():
    docker = DockerClient()
    docker.stop_all()
    docker.run('selenium/hub:2.53.0', bind_ports={4444: 4444}, name='selenium-hub')
    docker.run('selenium/node-firefox:2.53.0', links={'selenium-hub': 'hub'})
    containers = docker.get_running_containers()
    assert len(containers) >= 2
    docker.stop_all()
    assert len(docker.get_running_containers()) == 0


def test_docker_run_mysql():
    with MySqlDockerContainer() as mysql:
        conn = mysql.connection
        cur = conn.cursor()

        cur.execute("SELECT VERSION()")
        row = cur.fetchone()
        print "server version:", row[0]
        cur.close()
        assert len(row) > 0


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
    print docker.get_running_containers()


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


def test_generic_container():
    selenium_chrome = {
        "image": "selenium/standalone-chrome:2.53.0",
        "bind_ports": {4444: 4444},
        "name": "selenium_chrome"
    }

    with GenericDockerContainer(selenium_chrome) as chrome:
        assert chrome.id
