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
import ipaddress
import os
import urllib
import urllib.parse
from os.path import exists
from pathlib import Path
from typing import Optional, Union

import docker
from docker.models.containers import Container, ContainerCollection

from testcontainers.core.labels import SESSION_ID, create_labels
from testcontainers.core.utils import default_gateway_ip, inside_container, setup_logger

LOGGER = setup_logger(__name__)
TC_FILE = ".testcontainers.properties"
TC_GLOBAL = Path.home() / TC_FILE


class DockerClient:
    """
    Thin wrapper around :class:`docker.DockerClient` for a more functional interface.
    """

    def __init__(self, **kwargs) -> None:
        docker_host = get_docker_host()

        if docker_host:
            LOGGER.info(f"using host {docker_host}")
            self.client = docker.DockerClient(base_url=docker_host)
        else:
            self.client = docker.from_env(**kwargs)
        self.client.api.headers["x-tc-sid"] = SESSION_ID

    @ft.wraps(ContainerCollection.run)
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
        # https://github.com/testcontainers/testcontainers-go/blob/dd76d1e39c654433a3d80429690d07abcec04424/docker.go#L644
        # if os env TC_HOST is set, use it
        host = os.environ.get("TC_HOST")
        if host:
            return host
        try:
            url = urllib.parse.urlparse(self.client.api.base_url)

        except ValueError:
            return None
        if "http" in url.scheme or "tcp" in url.scheme:
            return url.hostname
        if inside_container() and ("unix" in url.scheme or "npipe" in url.scheme):
            ip_address = default_gateway_ip()
            if ip_address:
                return ip_address
        return "localhost"


@ft.cache
def read_tc_properties() -> dict[str, str]:
    """
    Read the .testcontainers.properties for settings. (see the Java implementation for details)
    Currently we only support the ~/.testcontainers.properties but may extend to per-project variables later.

    :return: the merged properties from the sources.
    """
    tc_files = [item for item in [TC_GLOBAL] if exists(item)]
    if not tc_files:
        return {}
    settings = {}

    for file in tc_files:
        tuples = []
        with open(file) as contents:
            tuples = [line.split("=") for line in contents.readlines() if "=" in line]
            settings = {**settings, **{item[0].strip(): item[1].strip() for item in tuples}}
    return settings


def get_docker_host() -> Optional[str]:
    return read_tc_properties().get("tc.host") or os.getenv("DOCKER_HOST")
