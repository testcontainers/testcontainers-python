from deprecation import deprecated
from docker.models.containers import Container

from testcontainers.core.docker_client import DockerClient
from testcontainers.core.exceptions import ContainerStartException
from testcontainers.core.utils import setup_logger, inside_container

logger = setup_logger(__name__)


class DockerContainer(object):
    def __init__(self, image, **kwargs):
        self.env = {}
        self.ports = {}
        self.volumes = {}
        self.image = image
        self._docker = DockerClient()
        self._container = None
        self._command = None
        self._name = None
        self._kwargs = kwargs

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

    @deprecated(details='Use `with_kwargs`.')
    def with_kargs(self, **kargs) -> 'DockerContainer':
        return self.with_kwargs(**kargs)

    def with_kwargs(self, **kwargs) -> 'DockerContainer':
        self._kwargs = kwargs
        return self

    def start(self):
        logger.info("Pulling image %s", self.image)
        docker_client = self.get_docker_client()
        self._container = docker_client.run(self.image,
                                            command=self._command,
                                            detach=True,
                                            environment=self.env,
                                            ports=self.ports,
                                            name=self._name,
                                            volumes=self.volumes,
                                            **self._kwargs
                                            )
        logger.info("Container started: %s", self._container.short_id)
        return self

    def stop(self, force=True, delete_volume=True):
        self.get_wrapped_container().remove(force=force, v=delete_volume)

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __del__(self):
        """
        Try to remove the container in all circumstances
        """
        if self._container is not None:
            try:
                self.stop()
            except:  # noqa: E722
                pass

    def get_container_host_ip(self) -> str:
        # infer from docker host
        host = self.get_docker_client().host()
        if not host:
            return "localhost"

        # check testcontainers itself runs inside docker container
        if inside_container():
            # If newly spawned container's gateway IP address from the docker
            # "bridge" network is equal to detected host address, we should use
            # container IP address, otherwise fall back to detected host
            # address. Even it's inside container, we need to double check,
            # because docker host might be set to docker:dind, usually in CI/CD environment
            gateway_ip = self.get_docker_client().gateway_ip(self._container.id)

            if gateway_ip == host:
                return self.get_docker_client().bridge_ip(self._container.id)
            return gateway_ip
        return host

    def get_exposed_port(self, port) -> str:
        mapped_port = self.get_docker_client().port(self._container.id, port)
        if inside_container():
            gateway_ip = self.get_docker_client().gateway_ip(self._container.id)
            host = self.get_docker_client().host()

            if gateway_ip == host:
                return port
        return mapped_port

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

    def get_wrapped_container(self) -> Container:
        return self._container

    def get_docker_client(self) -> DockerClient:
        return self._docker

    def exec(self, command):
        if not self._container:
            raise ContainerStartException("Container should be started before")
        return self.get_wrapped_container().exec_run(command)
