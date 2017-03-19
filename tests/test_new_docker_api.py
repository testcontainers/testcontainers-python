import docker
from docker.models.containers import Container
from docker.models.images import Image, ImageCollection
from selenium import webdriver

from testcontainers.core.container import DockerContainer


class DockerCli(object):
    def __init__(self):
        self.client = docker.from_env()

    def run(self, image: str,
            command: str = None,
            detach: bool = False,
            name: str = None,
            stdout: bool = True,
            stderr: bool = False,
            remove: bool = False, **kwargs) -> Container:
        containers = cli.client.containers.list(all=True, filters={"name": "mysql"})
        self.remove(containers)

        return self.client.containers.run(image,
                                          command=command,
                                          stdout=stdout,
                                          stderr=stderr,
                                          remove=remove,
                                          detach=detach,
                                          name=name,
                                          **kwargs)

    def pull(self, name: str, **kwargs) -> Image:
        self.client.images.pull(name, **kwargs)

    def images(self) -> ImageCollection:
        return self.client.images

    def remove(self, containers):
        for c in containers:
            c.remove(force=True)


def test_docker():
    container = DockerContainer("spirogov/video_service", "latest").expose_port(8086, 8086)

    with container:
        driver = webdriver.Chrome(executable_path="/home/sergey/.wdm/chromedriver/2.28/chromedriver")
        driver.get("http://localhost:8086")
