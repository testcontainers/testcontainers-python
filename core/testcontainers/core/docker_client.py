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
import functools as ft
import importlib.metadata
import ipaddress
import os
import urllib
import urllib.parse
from collections.abc import Iterable
from typing import Callable, Optional, TypeVar, Union

import docker
from docker.models.containers import Container, ContainerCollection
from docker.models.images import Image, ImageCollection
from typing_extensions import ParamSpec

from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.labels import SESSION_ID, create_labels
from testcontainers.core.utils import default_gateway_ip, inside_container, parse_docker_auth_config, setup_logger

LOGGER = setup_logger(__name__)

_P = ParamSpec("_P")
_T = TypeVar("_T")


def _wrapped_container_collection(function: Callable[_P, _T]) -> Callable[_P, _T]:
    @ft.wraps(ContainerCollection.run)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        return function(*args, **kwargs)

    return wrapper


def _wrapped_image_collection(function: Callable[_P, _T]) -> Callable[_P, _T]:
    @ft.wraps(ImageCollection.build)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        return function(*args, **kwargs)

    return wrapper


class DockerClient:
    """
    Thin wrapper around :class:`docker.DockerClient` for a more functional interface.
    """

    def __init__(self, **kwargs) -> None:
        docker_host = get_docker_host()

        if docker_host:
            LOGGER.info(f"using host {docker_host}")
            os.environ["DOCKER_HOST"] = docker_host
            self.client = docker.from_env(**kwargs)
        else:
            self.client = docker.from_env(**kwargs)
        self.client.api.headers["x-tc-sid"] = SESSION_ID
        self.client.api.headers["User-Agent"] = "tc-python/" + importlib.metadata.version("testcontainers")

        if docker_auth_config := get_docker_auth_config():
            self.login(docker_auth_config)

    @_wrapped_container_collection
    def run(
        self,
        image: str,
        command: Optional[Union[str, list[str]]] = None,
        environment: Optional[dict] = None,
        ports: Optional[dict] = None,
        labels: Optional[dict[str, str]] = None,
        detach: bool = False,
        stdout: bool = True,
        stderr: bool = False,
        remove: bool = False,
        **kwargs,
    ) -> Container:
        # If the user has specified a network, we'll assume the user knows best
        if "network" not in kwargs and not get_docker_host():
            # Otherwise we'll try to find the docker host for dind usage.
            host_network = self.find_host_network()
            if host_network:
                kwargs["network"] = host_network
        container = self.client.containers.run(
            image,
            command=command,
            stdout=stdout,
            stderr=stderr,
            remove=remove,
            detach=detach,
            environment=environment,
            ports=ports,
            labels=create_labels(image, labels),
            **kwargs,
        )
        return container

    @_wrapped_image_collection
    def build(self, path: str, tag: str, rm: bool = True, **kwargs) -> tuple[Image, Iterable[dict]]:
        """
        Build a Docker image from a directory containing the Dockerfile.

        :return: A tuple containing the image object and the build logs.
        """
        image_object, image_logs = self.client.images.build(path=path, tag=tag, rm=rm, **kwargs)

        return image_object, image_logs

    def find_host_network(self) -> Optional[str]:
        """
        Try to find the docker host network.

        :return: The network name if found, None if not set.
        """
        # If we're docker in docker running on a custom network, we need to inherit the
        # network settings, so we can access the resulting container.
        try:
            docker_host = ipaddress.IPv4Address(self.host())
            # See if we can find the host on our networks
            for network in self.client.networks.list(filters={"type": "custom"}):
                if "IPAM" in network.attrs:
                    for config in network.attrs["IPAM"]["Config"]:
                        try:
                            subnet = ipaddress.IPv4Network(config["Subnet"])
                        except ipaddress.AddressValueError:
                            continue
                        if docker_host in subnet:
                            return network.name
        except ipaddress.AddressValueError:
            pass
        return None

    def port(self, container_id: str, port: int) -> int:
        """
        Lookup the public-facing port that is NAT-ed to :code:`port`.
        """
        port_mappings = self.client.api.port(container_id, port)
        if not port_mappings:
            raise ConnectionError(f"Port mapping for container {container_id} and port {port} is " "not available")
        return port_mappings[0]["HostPort"]

    def get_container(self, container_id: str) -> Container:
        """
        Get the container with a given identifier.
        """
        containers = self.client.api.containers(filters={"id": container_id})
        if not containers:
            raise RuntimeError(f"Could not get container with id {container_id}")
        return containers[0]

    def bridge_ip(self, container_id: str) -> str:
        """
        Get the bridge ip address for a container.
        """
        container = self.get_container(container_id)
        network_name = self.network_name(container_id)
        return container["NetworkSettings"]["Networks"][network_name]["IPAddress"]

    def network_name(self, container_id: str) -> str:
        """
        Get the name of the network this container runs on
        """
        container = self.get_container(container_id)
        name = container["HostConfig"]["NetworkMode"]
        if name == "default":
            return "bridge"
        return name

    def gateway_ip(self, container_id: str) -> str:
        """
        Get the gateway ip address for a container.
        """
        container = self.get_container(container_id)
        network_name = self.network_name(container_id)
        return container["NetworkSettings"]["Networks"][network_name]["Gateway"]

    def host(self) -> str:
        """
        Get the hostname or ip address of the docker host.
        """
        host = c.tc_host_override
        if host:
            return host
        try:
            url = urllib.parse.urlparse(self.client.api.base_url)

        except ValueError:
            return "localhost"
        if "http" in url.scheme or "tcp" in url.scheme:
            return url.hostname
        if inside_container() and ("unix" in url.scheme or "npipe" in url.scheme):
            ip_address = default_gateway_ip()
            if ip_address:
                return ip_address
        return "localhost"

    def login(self, docker_auth_config: str) -> None:
        """
        Login to a docker registry using the given auth config.
        """
        auth_config = parse_docker_auth_config(docker_auth_config)[0]  # Only using the first auth config
        login_info = self.client.login(**auth_config._asdict())
        LOGGER.debug(f"logged in using {login_info}")


def get_docker_host() -> Optional[str]:
    return c.tc_properties_get_tc_host() or os.getenv("DOCKER_HOST")


def get_docker_auth_config() -> Optional[str]:
    return c.docker_auth_config
