from testcontainers_python.docker_client import DockerClient


class Container(object):
    def __init__(self):
        self._docker = DockerClient()
        self._containers = []
        self._default_port = None

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
        for cont in self._containers:
            self._docker.remove(cont, True)


class GenericContainer(Container):
    def __init__(self, config):
        Container.__init__(self)
        self.config = config

    def start(self):
        """
        Start container without wait
        :return:
        """
        container = self._docker.run(**self.config)
        self._containers.append(container)
        return self

    @property
    def id(self):
        return self._containers[0]["Id"]
