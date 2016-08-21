from testcontainers.docker_client import DockerClient


class DockerContainer(object):
    def __init__(self):
        self._docker = DockerClient()

    def __enter__(self):
        return self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        raise NotImplementedError

    def stop(self):
        """
        Stop all spawned containers
        :return:
        """
        self._docker.remove_all_spawned()


class GenericDockerContainer(DockerContainer):
    def __init__(self, config):
        DockerContainer.__init__(self)
        self.container = None
        self.config = config

    def start(self):
        """
        Start container without wait
        :return:
        """
        self.container = self._docker.run(**self.config)
        return self

    @property
    def id(self):
        return self.container["Id"]
