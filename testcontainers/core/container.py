import blindspin
import crayons
from docker.models.containers import Container

from testcontainers.core.docker_client import DockerClient
from testcontainers.core.exceptions import ContainerStartException
from testcontainers.core.utils import is_windows, inside_container


class DockerContainer(object):
    def __init__(self, image, **kwargs):
        self._docker = DockerClient()
        self._container = None
        self._kwargs = {
            'detach': True,
            'environment': {}, 
            'ports': {}, 
            'volumes': {}, 
            'image': image,
            **kwargs,
            }

    def _with_map_entry(self, map_key, key, value) -> 'DockerContainer':
        if not self._kwargs.get(map_key, None) or not isinstance(self._kwargs.get(map_key), dict):
            self._kwargs[map_key] = {}

        self._kwargs[map_key][key] = value
        return self

    def with_env(self, key: str, value: str) -> 'DockerContainer':
        return self._with_map_entry('environment', key, value)

    def with_bind_ports(self, container: int,
                        host: int = None) -> 'DockerContainer':
        return self._with_map_entry('ports', container, host)

    def with_exposed_ports(self, *ports) -> 'DockerContainer':
        for port in list(ports):
            self._with_map_entry('ports', port, None)
        return self

    def with_kwargs(self, **kwargs) -> 'DockerContainer':
        self._kwargs = {**self._kwargs, **kwargs}
        return self

    def start(self):
        print("")
        print("{} {}".format(crayons.yellow("Pulling image"),
                             crayons.red(self._kwargs['image'])))
        with blindspin.spinner():
            docker_client = self.get_docker_client()
            self._container = docker_client.run(**self._kwargs)
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
        # if testcontainers itself runs in docker, get the newly spawned
        # container's IP address from the dockder "bridge" network
        if inside_container():
            return self.get_docker_client().bridge_ip(self._container.id)
        elif is_windows():
            return "localhost"
        else:
            return "0.0.0.0"

    def get_exposed_port(self, port) -> str:
        if inside_container():
            return port
        else:
            return self.get_docker_client().port(self._container.id, port)

    def with_command(self, command: str) -> 'DockerContainer':
        return self.with_kwargs(command=command)

    def with_name(self, name: str) -> 'DockerContainer':
        return self.with_kwargs(name=name)

    def with_volume_mapping(self, host: str, container: str,
                            mode: str = 'ro') -> 'DockerContainer':
        # '/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'}
        mapping = {'bind': container, 'mode': mode}
        return self._with_map_entry('volumes', host, mapping)

    def get_wrapped_contaner(self) -> Container:
        return self._container

    def get_docker_client(self) -> DockerClient:
        return self._docker

    def exec(self, command):
        if not self._container:
            raise ContainerStartException("Container should be started before")
        return self.get_wrapped_contaner().exec_run(command)
