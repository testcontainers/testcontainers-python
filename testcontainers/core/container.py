import blindspin
import crayons

from testcontainers.core.docker_client import DockerClient
from testcontainers.core.utils import is_windows


class DockerContainer(object):
    def __init__(self, image):
        self.env = {}
        self.ports = {}
        self._docker = DockerClient()
        self.image = image
        self._container = None

    def add_env(self, key, value):
        self.env[key] = value
        return self

    def expose_port(self, container, host=None):
        self.ports[container] = host
        return self

    def _configure(self):
        pass

    def start(self):
        self._configure()
        print("")
        print(crayons.yellow("Pulling an image {}".format(self.image)))
        with blindspin.spinner():
            self._container = self._docker.run(self.image,
                                               detach=True,
                                               environment=self.env,
                                               ports=self.ports,
                                               publish_all_ports=True)
        print("")
        print("Container started: ", crayons.yellow(self._container.id, bold=True))
        return self

    def stop(self):
        self._container.remove(force=True)

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def get_container_host_ip(self) -> str:
        if is_windows():
            return "localhost"
        else:
            return "0.0.0.0"

    def get_exposed_port(self, port) -> str:
        return self._docker.port(self._container.id, port)
