from testcontainers_python.docker_client import DockerClient


class GenericContainer(object):
    def __init__(self):
        self._docker = DockerClient()
        self._containers = []

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
