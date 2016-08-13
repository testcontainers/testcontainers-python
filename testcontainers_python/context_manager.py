from testcontainers_python import config
from testcontainers_python.docker_client import DockerClient


class docker_client(object):
    def __init__(self, base_url=config.docker_base_url):
        self._docker = DockerClient(base_url)

    def __enter__(self):
        return self._docker

    def __exit__(self, type, value, traceback):
        for cont in self._docker.get_containers():
            self._docker.stop(cont)
            self._docker.remove(cont, True)
