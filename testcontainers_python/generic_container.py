from testcontainers_python.docker_client import DockerClient


class GenericContainer(object):
    def __init__(self):
        self._docker = DockerClient()
        self._containers = []
        self._default_port = None

    def __enter__(self):
        return self._docker

    def __exit__(self, type, value, traceback):
        for container in self._docker.get_containers():
            self._docker.stop(container)

    def start(self):
        raise NotImplementedError

    def stop(self):
        """
        Stop all spawned containers
        :return:
        """
        for cont in self._containers:
            self._docker.remove(cont, True)
