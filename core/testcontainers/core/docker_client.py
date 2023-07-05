#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import atexit
import docker
from docker.errors import NotFound
from docker.models.containers import Container, ContainerCollection
import functools as ft
import os
from typing import List, Optional, Union
import urllib
import socket
import ipaddress

from .utils import default_gateway_ip, inside_container, setup_logger


LOGGER = setup_logger(__name__)


def _stop_container(container: Container) -> None:
    try:
        container.stop()
    except NotFound:
        pass
    except Exception as ex:
        LOGGER.warning("failed to shut down container %s with image %s: %s", container.id,
                       container.image, ex)


class DockerClient:
    """
    Thin wrapper around :class:`docker.DockerClient` for a more functional interface.
    """
    def __init__(self, **kwargs) -> None:
        self.client = docker.from_env(**kwargs)

    @ft.wraps(ContainerCollection.run)
    def run(self, image: str, command: Union[str, List[str]] = None,
            environment: Optional[dict] = None, ports: Optional[dict] = None,
            detach: bool = False, stdout: bool = True, stderr: bool = False, remove: bool = False,
            **kwargs) -> Container:
        # If we're docker in docker running on a custom network, we need to inherit the
        # network, so we can access the resulting container. Unless the user has specified
        # a network, then we'll assume the user knows best
        if 'network' not in kwargs and not os.getenv('DOCKER_HOST'):
            # See if we can find the host on our networks
            host_network = None
            try:
                docker_host = ipaddress.IPv4Address(self.host())
                for network in self.client.networks.list(filters={'type': 'custom'}):
                    if 'IPAM' in network.attrs:
                        for config in network.attrs['IPAM']['Config']:
                            try:
                              subnet = ipaddress.IPv4Network(config['Subnet'])
                            except ipaddress.AddressValueError:
                                continue
                            if docker_host in subnet:
                                host_network = network.name
                                break
                        if host_network:
                            break
                if host_network:
                    kwargs['network'] = host_network

            except ipaddress.AddressValueError:
                pass
        container = self.client.containers.run(
            image, command=command, stdout=stdout, stderr=stderr, remove=remove, detach=detach,
            environment=environment, ports=ports, **kwargs
        )
        if detach:
            atexit.register(_stop_container, container)
        return container

    def port(self, container_id: str, port: int) -> int:
        """
        Lookup the public-facing port that is NAT-ed to :code:`port`.
        """
        port_mappings = self.client.api.port(container_id, port)
        if not port_mappings:
            raise ConnectionError(f'Port mapping for container {container_id} and port {port} is '
                                  'not available')
        return port_mappings[0]["HostPort"]

    def get_container(self, container_id: str) -> Container:
        """
        Get the container with a given identifier.
        """
        containers = self.client.api.containers(filters={'id': container_id})
        if not containers:
            raise RuntimeError(f'Could not get container with id {container_id}')
        return containers[0]

    def bridge_ip(self, container_id: str) -> str:
        """
        Get the bridge ip address for a container.
        """
        container = self.get_container(container_id)
        network_name = self.network_name(container_id)
        return container['NetworkSettings']['Networks'][network_name]['IPAddress']

    def network_name(self, container_id: str) -> str:
        """
        Get the name of the network this container runs on
        """
        container = self.get_container(container_id)
        name = container['HostConfig']['NetworkMode']
        if name == 'default':
            return 'bridge'
        return name

    def gateway_ip(self, container_id: str) -> str:
        """
        Get the gateway ip address for a container.
        """
        container = self.get_container(container_id)
        network_name = self.network_name(container_id)
        return container['NetworkSettings']['Networks'][network_name]['Gateway']

    def host(self) -> str:
        """
        Get the hostname or ip address of the docker host.
        """
        # https://github.com/testcontainers/testcontainers-go/blob/dd76d1e39c654433a3d80429690d07abcec04424/docker.go#L644
        # if os env TC_HOST is set, use it
        host = os.environ.get('TC_HOST')
        if host:
            return host
        try:
            url = urllib.parse.urlparse(self.client.api.base_url)

        except ValueError:
            return None
        if 'http' in url.scheme or 'tcp' in url.scheme:
            return url.hostname
        if 'unix' in url.scheme or 'npipe' in url.scheme:
            if inside_container():
                ip_address = default_gateway_ip()
                if ip_address:
                    return ip_address
        return "localhost"
