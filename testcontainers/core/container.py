from testcontainers.core.docker_client import DockerClient


class DockerContainer(object):
    def __init__(self, image, version):
        self.env = {}
        self.ports = {}
        self._docker = DockerClient()
        self.image = "{}:{}".format(image, version)
        self._container = None

    def add_env(self, key, value):
        self.env[key] = value

    def expose_port(self, container, host):
        self.ports[container] = host

    def _configure(self):
        pass

    def start(self):
        self._configure()
        self._container = self._docker.run(self.image,
                                           detach=True,
                                           environment=self.env,
                                           #ports=self.ports,
                                           publish_all_ports=True)
        return self

    def stop(self):
        self._container.remove(force=True)

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def get_container_host_ip(self) -> str:
        return "0.0.0.0"

    def get_exposed_port(self, port) -> str:
        return self._docker.port(self._container.id, port)
