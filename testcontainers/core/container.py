import blindspin
import crayons
from docker.models.containers import Container

from testcontainers.core.docker_client import DockerClient
from testcontainers.core.exceptions import ContainerStartException
from testcontainers.core.utils import is_windows


class DockerContainer(object):
    def __init__(self, image):
        self.env = {}
        self.ports = {}
        self.volumes = {}
        self.image = image
        self._docker = DockerClient()
        self._container = None
        self._command = None
        self._name = None

    def with_env(self, key: str, value: str) -> 'DockerContainer':
        self.env[key] = value
        return self

    def with_bind_ports(self, container: int,
                        host: int = None) -> 'DockerContainer':
        self.ports[container] = host
        return self

    def with_exposed_ports(self, *ports) -> 'DockerContainer':
        for port in list(ports):
            self.ports[port] = None
        return self

    def start(self):
        print("")
        print("{} {}".format(crayons.yellow("Pulling image"),
                             crayons.red(self.image)))
        with blindspin.spinner():
            docker_client = self.get_docker_client()
            self._container = docker_client.run(self.image,
                                                command=self._command,
                                                detach=True,
                                                environment=self.env,
                                                ports=self.ports,
                                                name=self._name,
                                                volumes=self.volumes)
        print("")
        print("Container started: ",
              crayons.yellow(self._container.short_id, bold=True))
        return self

    def stop(self, force=True, delete_volume=True):
        self.get_wrapped_contaner().remove(force=force, v=delete_volume)

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
        return self.get_docker_client().port(self._container.id, port)

    def with_command(self, command: str) -> 'DockerContainer':
        self._command = command
        return self

    def with_name(self, name: str) -> 'DockerContainer':
        self._name = name
        return self

    def with_volume_mapping(self, host: str, container: str,
                            mode: str = 'ro') -> 'DockerContainer':
        # '/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'}
        mapping = {'bind': container, 'mode': mode}
        self.volumes[host] = mapping
        return self

    def get_wrapped_contaner(self) -> Container:
        return self._container

    def get_docker_client(self) -> DockerClient:
        return self._docker

    def exec(self, command):
        if not self._container:
            raise ContainerStartException("Container should be started before")
        return self.get_wrapped_contaner().exec_run(command)
