import docker
from docker.models.containers import Container
from docker.models.images import Image, ImageCollection


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


cli = DockerCli()

container = cli.run("mysql:5.7",
                    environment=["MYSQL_ROOT_PASSWORD=secret"],
                    detach=True,
                    name="mysql")

print(container.logs())
print(container.id)
