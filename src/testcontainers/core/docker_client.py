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
from __future__ import annotations

import contextlib
import functools
import importlib.metadata
import ipaddress
import os
import socket
import urllib
import urllib.parse
from collections.abc import Iterable, Iterator, Mapping
from typing import TYPE_CHECKING, Any, Literal, Optional, TypedDict, Union, cast, overload

import docker
from docker.context import ContextAPI
from docker.models.containers import Container
from docker.models.images import Image
from typing_extensions import Unpack

from testcontainers.core import utils
from testcontainers.core.auth import DockerAuthInfo, parse_docker_auth_config
from testcontainers.core.config import ConnectionMode
from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.inspect import ContainerInspectInfo
from testcontainers.core.labels import SESSION_ID, create_labels

if TYPE_CHECKING:
    from io import StringIO
    from typing import IO

    from docker._types import JSON, ContainerWeightDevice  # only exists in docker-stubs, not at runtime
    from docker.models.containers import _RestartPolicy
    from docker.models.images import _ContainerLimits
    from docker.models.networks import Network as DockerNetwork
    from docker.types import EndpointConfig
    from docker.types.containers import DeviceRequest, LogConfig, Ulimit
    from docker.types.services import Mount

    class _RunKwargs(TypedDict, total=False):
        """Extra keyword arguments for :meth:`DockerClient.run`.

        Mirrors the parameters of :meth:`docker.models.containers.ContainerCollection.run`
        that are not declared explicitly on :meth:`DockerClient.run`. All fields are optional
        (``total=False``); omitting a field lets the Docker daemon apply its default.
        """

        auto_remove: bool
        blkio_weight_device: Optional[list[ContainerWeightDevice]]
        blkio_weight: Optional[int]
        cap_add: Optional[list[str]]
        cap_drop: Optional[list[str]]
        cgroup_parent: Optional[str]
        cgroupns: Optional[Literal["private", "host"]]
        cpu_count: Optional[int]
        cpu_percent: Optional[int]
        cpu_period: Optional[int]
        cpu_quota: Optional[int]
        cpu_rt_period: Optional[int]
        cpu_rt_runtime: Optional[int]
        cpu_shares: Optional[int]
        cpuset_cpus: Optional[str]
        cpuset_mems: Optional[str]
        device_cgroup_rules: Optional[list[str]]
        device_read_bps: Optional[list[Mapping[str, Union[str, int]]]]
        device_read_iops: Optional[list[Mapping[str, Union[str, int]]]]
        device_write_bps: Optional[list[Mapping[str, Union[str, int]]]]
        device_write_iops: Optional[list[Mapping[str, Union[str, int]]]]
        devices: Optional[list[str]]
        device_requests: Optional[list[DeviceRequest]]
        dns: Optional[list[str]]
        dns_opt: Optional[list[str]]
        dns_search: Optional[list[str]]
        domainname: Optional[Union[str, list[str]]]
        entrypoint: Optional[Union[str, list[str]]]
        extra_hosts: Optional[dict[str, str]]
        group_add: Optional[Iterable[Union[str, int]]]
        healthcheck: Optional[dict[str, Any]]
        hostname: Optional[str]
        init: Optional[bool]
        init_path: Optional[str]
        ipc_mode: Optional[str]
        isolation: Optional[str]
        kernel_memory: Optional[Union[str, int]]
        links: Optional[
            Union[dict[str, str], dict[str, None], dict[str, Union[str, None]], Iterable[tuple[str, Union[str, None]]]]
        ]
        log_config: Optional[LogConfig]
        lxc_conf: Optional[dict[str, str]]
        mac_address: Optional[str]
        mem_limit: Optional[Union[str, int]]
        mem_reservation: Optional[Union[str, int]]
        mem_swappiness: Optional[int]
        memswap_limit: Optional[Union[str, int]]
        mounts: Optional[list[Mount]]
        name: Optional[str]
        nano_cpus: Optional[int]
        network: Optional[str]
        network_disabled: bool
        network_mode: Optional[str]
        networking_config: Optional[dict[str, EndpointConfig]]
        oom_kill_disable: bool
        oom_score_adj: Optional[int]
        pid_mode: Optional[str]
        pids_limit: Optional[int]
        platform: Optional[str]
        privileged: bool
        publish_all_ports: bool
        read_only: Optional[bool]
        restart_policy: Optional[_RestartPolicy]
        runtime: Optional[str]
        security_opt: Optional[list[str]]
        shm_size: Optional[Union[str, int]]
        stdin_open: bool
        stop_signal: Optional[str]
        storage_opt: Optional[dict[str, str]]
        stream: bool
        sysctls: Optional[dict[str, str]]
        tmpfs: Optional[dict[str, str]]
        tty: bool
        ulimits: Optional[list[Ulimit]]
        use_config_proxy: Optional[bool]
        user: Optional[Union[str, int]]
        userns_mode: Optional[str]
        uts_mode: Optional[str]
        version: Optional[str]
        volume_driver: Optional[str]
        volumes: Optional[Union[dict[str, dict[str, str]], list[str]]]
        volumes_from: Optional[list[str]]
        working_dir: Optional[str]

    class _BuildKwargs(TypedDict, total=False):
        """Extra keyword arguments for :meth:`DockerClient.build`.

        Mirrors the parameters of :meth:`docker.models.images.ImageCollection.build`
        that are not declared explicitly on :meth:`DockerClient.build`. All fields are optional;
        """

        fileobj: Union[StringIO, IO[bytes]]
        quiet: bool
        nocache: bool
        timeout: int
        custom_context: bool
        encoding: str
        pull: bool
        forcerm: bool
        dockerfile: str
        buildargs: dict[str, Any]
        container_limits: _ContainerLimits
        shmsize: int
        labels: dict[str, Any]
        cache_from: list[str]
        target: str
        network_mode: str
        squash: bool
        extra_hosts: Union[list[str], dict[str, str]]
        platform: str
        isolation: str
        use_config_proxy: bool


LOGGER = utils.setup_logger(__name__)


class DockerClient:
    """
    Thin wrapper around :class:`docker.DockerClient` for a more functional interface.
    """

    client: docker.DockerClient

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

    @overload
    def run(
        self,
        image: str,
        command: Optional[Union[str, list[str]]] = None,
        *,
        detach: Literal[True],
        environment: Optional[Union[dict[str, str], list[str]]] = None,
        ports: Optional[Mapping[str, Union[int, list[int], tuple[str, int], None]]] = None,
        labels: Optional[dict[str, str]] = None,
        stdout: bool = True,
        stderr: bool = False,
        remove: bool = False,
        **kwargs: Unpack[_RunKwargs],
    ) -> Container: ...

    @overload
    def run(
        self,
        image: str,
        command: Optional[Union[str, list[str]]] = None,
        *,
        detach: Literal[False] = False,
        environment: Optional[Union[dict[str, str], list[str]]] = None,
        ports: Optional[Mapping[str, Union[int, list[int], tuple[str, int], None]]] = None,
        labels: Optional[dict[str, str]] = None,
        stdout: bool = True,
        stderr: bool = False,
        remove: bool = False,
        **kwargs: Unpack[_RunKwargs],
    ) -> bytes: ...

    def run(
        self,
        image: str,
        command: Optional[Union[str, list[str]]] = None,
        *,
        detach: bool = False,
        environment: Optional[Union[dict[str, str], list[str]]] = None,
        ports: Optional[Mapping[str, Union[int, list[int], tuple[str, int], None]]] = None,
        labels: Optional[dict[str, str]] = None,
        stdout: bool = True,
        stderr: bool = False,
        remove: bool = False,
        **kwargs: Unpack[_RunKwargs],
    ) -> Union[Container, bytes]:
        # If the user has specified a network, we'll assume the user knows best
        if "network" not in kwargs and not get_docker_host():
            # Otherwise we'll try to find the docker host for dind usage.
            host_network = self.find_host_network()
            if host_network:
                kwargs["network"] = host_network
        if detach:
            return self.client.containers.run(
                image,
                command=command,
                stdout=stdout,
                stderr=stderr,
                remove=remove,
                detach=True,
                environment=environment,
                ports=ports,
                labels=create_labels(image, labels),
                **kwargs,
            )
        else:
            return self.client.containers.run(
                image,
                command=command,
                stdout=stdout,
                stderr=stderr,
                remove=remove,
                detach=False,
                environment=environment,
                ports=ports,
                labels=create_labels(image, labels),
                **kwargs,
            )

    def create(
        self,
        image: str,
        command: Optional[Union[str, list[str]]] = None,
        environment: Optional[dict[str, str]] = None,
        ports: Optional[Mapping[str, Union[int, list[int], tuple[str, int], None]]] = None,
        labels: Optional[dict[str, str]] = None,
        detach: bool = False,
        **kwargs: Unpack[_RunKwargs],
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
            detach=detach,
            **kwargs,
        )
        return container

    def start(self, container: Container) -> None:
        """Start a previously created container."""
        container.start()

    def build(
        self, path: str, tag: Optional[str] = None, rm: bool = True, **kwargs: Unpack[_BuildKwargs]
    ) -> tuple[Image, Iterator[JSON]]:
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

    def client_networks_create(self, name: str, param: dict[str, Any]) -> DockerNetwork:
        labels = create_labels("", param.get("labels"))
        return self.client.networks.create(name, **{**param, "labels": labels})

    def get_container_inspect_info(self, container_id: str) -> ContainerInspectInfo:
        """Get container inspect information with fresh data."""
        container = self.client.containers.get(container_id)
        return ContainerInspectInfo.from_dict(container.attrs)

    def find_container_by_hash(self, hash_: str) -> Union[Container, None]:
        for container in self.client.containers.list(all=True):
            if container.labels.get("hash", None) == hash_:
                return container
        return None


def get_docker_host() -> Optional[str]:
    host = c.tc_properties_get_tc_host() or os.getenv("DOCKER_HOST") or _get_docker_host_from_context()
    if host:
        return _sanitize_docker_host(host)
    return None


def _get_docker_host_from_context() -> Optional[str]:
    """
    Look up the docker host from the current docker context (e.g. as set by``docker context use``).
    This allows users with a remote docker host configured via docker contexts to use testcontainers
    without having to additionally export ``DOCKER_HOST``.
    """
    try:
        context = ContextAPI.get_current_context()
    except Exception as e:
        LOGGER.debug(f"failed to read current docker context: {e}")
        return None
    if context is None:
        return None
    host = context.Host
    # The default context points at the local unix socket / named pipe; let
    # docker-py fall back to its own defaults in that case.
    if not host or context.Name == "default":
        return None
    return host


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


@functools.lru_cache(maxsize=1)
def is_podman() -> bool:
    """Detect whether the configured Docker daemon is actually Podman.

    The result is cached for the lifetime of the process: detection requires a
    daemon round-trip, and this helper is invoked at test-collection time via
    ``pytest.mark.skipif`` decorators.
    """
    try:
        # Build the client directly rather than via DockerClient() so we avoid
        # the constructor's side effects (registry login). We still resolve the
        # host the same way DockerClient does so that hosts coming from the
        # docker context (and SSH connections) are detected correctly.
        docker_host = get_docker_host()
        if docker_host:
            client_kwargs: dict[str, Any] = {"base_url": docker_host}
            if docker_host.startswith("ssh://"):
                # Mirror DockerClient: use the shell SSH client to avoid paramiko
                # failures under pytest stdin capture.
                client_kwargs["use_ssh_client"] = True
            version = docker.DockerClient(**client_kwargs).version()
        else:
            version = docker.from_env().version()
    except Exception as e:
        LOGGER.debug(f"is_podman: failed to query daemon version: {e}")
        return False

    # Prefer the top-level Platform.Name field (matches testcontainers-go).
    platform_name = (version.get("Platform") or {}).get("Name", "")
    if "podman" in platform_name.lower():
        return True
    # Fall back to scanning the Components array for older podman versions.
    return any("podman" in comp.get("Name", "").lower() for comp in version.get("Components") or [])


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
