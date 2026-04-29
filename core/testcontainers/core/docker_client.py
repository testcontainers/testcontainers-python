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
import contextlib
import functools as ft
import importlib.metadata
import ipaddress
import os
import socket
import urllib
import urllib.parse
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, Union, cast

import docker
from docker.models.containers import Container, ContainerCollection
from docker.models.images import Image, ImageCollection
from typing_extensions import ParamSpec

from testcontainers.core import utils
from testcontainers.core.auth import DockerAuthInfo, parse_docker_auth_config
from testcontainers.core.config import ConnectionMode
from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.inspect import ContainerInspectInfo
from testcontainers.core.labels import SESSION_ID, create_labels

if TYPE_CHECKING:
    from docker.models.networks import Network as DockerNetwork

LOGGER = utils.setup_logger(__name__)

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

    def __init__(self, **kwargs: Any) -> None:
        docker_host = get_docker_host()

        if docker_host:
            LOGGER.info(f"using host {docker_host}")
            os.environ["DOCKER_HOST"] = docker_host
            # Use shell-based SSH client instead of paramiko to avoid conflicts with pytest stdin capture
            # (paramiko's invoke library fails when reading from captured stdin).
            if docker_host.startswith("ssh://"):
                kwargs.setdefault("use_ssh_client", True)

        self.client = docker.from_env(**kwargs)
        self.client.api.headers["x-tc-sid"] = SESSION_ID
        self.client.api.headers["User-Agent"] = "tc-python/" + importlib.metadata.version("testcontainers")

        # Verify if we have a docker auth config and login if we do
        if docker_auth_config := get_docker_auth_config():
            LOGGER.debug(f"DOCKER_AUTH_CONFIG found: {docker_auth_config}")
            if auth_config := parse_docker_auth_config(docker_auth_config):
                self.login(auth_config[0])  # Only using the first auth config)

    @_wrapped_container_collection
    def run(
        self,
        image: str,
        command: Optional[Union[str, list[str]]] = None,
        environment: Optional[dict[str, str]] = None,
        ports: Optional[dict[int, Optional[int]]] = None,
        labels: Optional[dict[str, str]] = None,
        detach: bool = False,
        stdout: bool = True,
        stderr: bool = False,
        remove: bool = False,
        **kwargs: Any,
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

    @_wrapped_container_collection
    def create(
        self,
        image: str,
        command: Optional[Union[str, list[str]]] = None,
        environment: Optional[dict[str, str]] = None,
        ports: Optional[dict[int, Optional[int]]] = None,
        labels: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> Container:
        """Create a container without starting it, pulling the image first if not present locally."""
        if "network" not in kwargs and not get_docker_host():
            host_network = self.find_host_network()
            if host_network:
                kwargs["network"] = host_network

        try:
            # This is more or less a replication of what the self.client.containers.start does internally
            self.client.images.get(image)
        except docker.errors.ImageNotFound:
            self.client.images.pull(image)

        container = self.client.containers.create(
            image,
            command=command,
            environment=environment,
            ports=ports,
            labels=create_labels(image, labels),
            **kwargs,
        )
        return container

    @_wrapped_container_collection
    def start(self, container: Container) -> None:
        """Start a previously created container."""
        container.start()

    @_wrapped_image_collection
    def build(
        self, path: str, tag: Optional[str], rm: bool = True, **kwargs: Any
    ) -> tuple[Image, Iterable[dict[str, Any]]]:
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

        # first to try to find the network the container runs in, if we can determine
        container_id = utils.get_running_in_container_id()
        if container_id:
            with contextlib.suppress(Exception):
                return self.network_name(container_id)

        # if this results nothing, try to determine the network based on the
        # docker_host
        try:
            host_ip = socket.gethostbyname(self.host())
            docker_host = ipaddress.IPv4Address(host_ip)
            # See if we can find the host on our networks
            for network in self.client.networks.list(filters={"type": "custom"}):
                if "IPAM" in network.attrs:
                    for config in network.attrs["IPAM"]["Config"]:
                        try:
                            subnet = ipaddress.IPv4Network(config["Subnet"])
                        except ipaddress.AddressValueError:
                            continue
                        if docker_host in subnet:
                            return cast("str", network.name)
        except (ipaddress.AddressValueError, OSError):
            pass
        return None

    def port(self, container_id: str, port: int) -> str:
        """
        Lookup the public-facing port that is NAT-ed to :code:`port`.
        """
        port_mappings = self.client.api.port(container_id, port)
        if not port_mappings:
            raise ConnectionError(f"Port mapping for container {container_id} and port {port} is not available")
        return cast("str", port_mappings[0]["HostPort"])

    def get_container(self, container_id: str) -> dict[str, Any]:
        """
        Get the container with a given identifier.
        """
        containers = self.client.api.containers(all=True, filters={"id": container_id})
        if not containers:
            raise RuntimeError(f"Could not get container with id {container_id}")
        return cast("dict[str, Any]", containers[0])

    def bridge_ip(self, container_id: str) -> str:
        """
        Get the bridge ip address for a container.
        """
        container = self.get_container(container_id)
        network_name = self.network_name(container_id)
        return str(container["NetworkSettings"]["Networks"][network_name]["IPAddress"])

    def network_name(self, container_id: str) -> str:
        """
        Get the name of the network this container runs on
        """
        container = self.get_container(container_id)
        name = str(container["HostConfig"]["NetworkMode"])
        if name == "default":
            return "bridge"
        return name

    def gateway_ip(self, container_id: str) -> str:
        """
        Get the gateway ip address for a container.
        """
        container = self.get_container(container_id)
        network_name = self.network_name(container_id)
        return str(container["NetworkSettings"]["Networks"][network_name]["Gateway"])

    def get_connection_mode(self) -> ConnectionMode:
        """
        Determine the connection mode.

        See https://github.com/testcontainers/testcontainers-python/issues/475#issuecomment-2407250970
        """
        if c.connection_mode_override:
            return c.connection_mode_override
        localhosts = {"localhost", "127.0.0.1", "::1"}
        if not utils.inside_container() or self.host() not in localhosts:
            # if running not inside a container or with a non-local docker client,
            # connect ot the docker host per default
            return ConnectionMode.docker_host
        elif self.find_host_network():
            # a host network could be determined, indicator for DooD,
            # so we should connect to the bridge_ip as the container we run in
            # and the one we started are connected to the same network
            # that might have no access to either docker_host or the gateway
            return ConnectionMode.bridge_ip
        # default for DinD
        return ConnectionMode.gateway_ip

    def host(self) -> str:
        """
        Get the hostname or ip address of the docker host.
        """
        host = c.tc_host_override
        if host:
            return host

        # For SSH-based connections, the Docker SDK rewrites base_url to
        # "http+docker://ssh" which loses the original hostname.
        # Extract it from the original DOCKER_HOST instead.
        ssh_host = get_docker_host_hostname()
        if ssh_host:
            return ssh_host

        try:
            url = urllib.parse.urlparse(self.client.api.base_url)
        except ValueError:
            return "localhost"

        is_http_scheme = "http" in url.scheme
        is_tcp_scheme_with_hostname = "tcp" in url.scheme and url.hostname
        if is_http_scheme or is_tcp_scheme_with_hostname:
            # see https://github.com/testcontainers/testcontainers-python/issues/415
            hostname = url.hostname
            if not hostname or (hostname == "localnpipe" and utils.is_windows()):
                return "localhost"
            return cast("str", url.hostname)
        if utils.inside_container() and ("unix" in url.scheme or "npipe" in url.scheme):
            ip_address = utils.default_gateway_ip()
            if ip_address:
                return ip_address
        return "localhost"

    def login(self, auth_config: DockerAuthInfo) -> None:
        """
        Login to a docker registry using the given auth config.
        """
        login_info = self.client.login(**auth_config._asdict())
        LOGGER.debug(f"logged in using {login_info}")

    def client_networks_create(self, name: str, param: dict[str, Any]) -> "DockerNetwork":
        labels = create_labels("", param.get("labels"))
        return self.client.networks.create(name, **{**param, "labels": labels})

    def get_container_inspect_info(self, container_id: str) -> "ContainerInspectInfo":
        """Get container inspect information with fresh data."""
        container = self.client.containers.get(container_id)
        return ContainerInspectInfo.from_dict(container.attrs)


def get_docker_host() -> Optional[str]:
    host = c.tc_properties_get_tc_host() or os.getenv("DOCKER_HOST")
    if host:
        return _sanitize_docker_host(host)
    return None


def get_docker_host_hostname() -> Optional[str]:
    """Extract the remote hostname from an SSH-based DOCKER_HOST.

    Returns the hostname (e.g. '192.168.1.42') when DOCKER_HOST is an ssh:// URL, or None otherwise.
    """
    docker_host = get_docker_host()
    if docker_host and docker_host.startswith("ssh://"):
        parsed = urllib.parse.urlparse(docker_host)
        if parsed.hostname:
            return parsed.hostname
    return None


def is_ssh_docker_host() -> bool:
    """Check if the current DOCKER_HOST is an SSH-based connection."""
    return get_docker_host_hostname() is not None


def _sanitize_docker_host(docker_host: str) -> str:
    """
    Sanitize the DOCKER_HOST value for compatibility with the Docker SDK.

    Strips path components from ``ssh://`` URLs because the Docker SDK
    does not support them.  A lone trailing ``/`` is treated as
    equivalent to no path and silently normalised without a warning.
    """
    if docker_host.startswith("ssh://"):
        parsed = urllib.parse.urlparse(docker_host)
        if parsed.path and parsed.path != "/":
            sanitized = urllib.parse.urlunparse(parsed._replace(path=""))
            LOGGER.warning(
                "Stripped path from SSH DOCKER_HOST (unsupported by Docker SDK): %s -> %s",
                docker_host,
                sanitized,
            )
            return sanitized
        if parsed.path == "/":
            # Trailing slash is harmless — strip quietly.
            return urllib.parse.urlunparse(parsed._replace(path=""))
    return docker_host


def get_docker_auth_config() -> Optional[str]:
    return c.docker_auth_config
