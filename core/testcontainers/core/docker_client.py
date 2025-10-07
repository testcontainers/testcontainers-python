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
from dataclasses import dataclass, fields, is_dataclass
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, Union, cast

import docker
from docker.models.containers import Container, ContainerCollection
from docker.models.images import Image, ImageCollection
from typing_extensions import ParamSpec

from testcontainers.core import utils
from testcontainers.core.auth import DockerAuthInfo, parse_docker_auth_config
from testcontainers.core.config import ConnectionMode
from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.labels import SESSION_ID, create_labels

if TYPE_CHECKING:
    from docker.models.networks import Network as DockerNetwork

LOGGER = utils.setup_logger(__name__)

_P = ParamSpec("_P")
_T = TypeVar("_T")
_IPT = TypeVar("_IPT")


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
            self.client = docker.from_env(**kwargs)
        else:
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


def get_docker_host() -> Optional[str]:
    return c.tc_properties_get_tc_host() or os.getenv("DOCKER_HOST")


def get_docker_auth_config() -> Optional[str]:
    return c.docker_auth_config


# Docker Engine API data structures


@dataclass
class ContainerLog:
    """Container health check log entry."""

    Start: Optional[str] = None
    End: Optional[str] = None
    ExitCode: Optional[int] = None
    Output: Optional[str] = None


@dataclass
class ContainerHealth:
    """Container health check information."""

    Status: Optional[str] = None
    FailingStreak: Optional[int] = None
    Log: Optional[list[ContainerLog]] = None


@dataclass
class ContainerState:
    """Container state information."""

    Status: Optional[str] = None
    Running: Optional[bool] = None
    Paused: Optional[bool] = None
    Restarting: Optional[bool] = None
    OOMKilled: Optional[bool] = None
    Dead: Optional[bool] = None
    Pid: Optional[int] = None
    ExitCode: Optional[int] = None
    Error: Optional[str] = None
    StartedAt: Optional[str] = None
    FinishedAt: Optional[str] = None
    Health: Optional[ContainerHealth] = None


@dataclass
class ContainerPlatform:
    """Platform information for image manifest."""

    architecture: Optional[str] = None
    os: Optional[str] = None
    variant: Optional[str] = None


@dataclass
class ContainerImageManifestDescriptor:
    """Image manifest descriptor."""

    mediaType: Optional[str] = None
    digest: Optional[str] = None
    size: Optional[int] = None
    urls: Optional[list[str]] = None
    annotations: Optional[dict[str, str]] = None
    data: Optional[Any] = None
    platform: Optional[ContainerPlatform] = None
    artifactType: Optional[str] = None


@dataclass
class ContainerBlkioWeightDevice:
    """Block IO weight device configuration."""

    Path: Optional[str] = None
    Weight: Optional[int] = None


@dataclass
class ContainerBlkioDeviceRate:
    """Block IO device rate configuration."""

    Path: Optional[str] = None
    Rate: Optional[int] = None


@dataclass
class ContainerDeviceMapping:
    """Device mapping configuration."""

    PathOnHost: Optional[str] = None
    PathInContainer: Optional[str] = None
    CgroupPermissions: Optional[str] = None


@dataclass
class ContainerDeviceRequest:
    """Device request configuration."""

    Driver: Optional[str] = None
    Count: Optional[int] = None
    DeviceIDs: Optional[list[str]] = None
    Capabilities: Optional[list[list[str]]] = None
    Options: Optional[dict[str, str]] = None


@dataclass
class ContainerUlimit:
    """Ulimit configuration."""

    Name: Optional[str] = None
    Soft: Optional[int] = None
    Hard: Optional[int] = None


@dataclass
class ContainerLogConfig:
    """Logging configuration."""

    Type: Optional[str] = None
    Config: Optional[dict[str, str]] = None


@dataclass
class ContainerPortBinding:
    """Port binding configuration."""

    HostIp: Optional[str] = None
    HostPort: Optional[str] = None


@dataclass
class ContainerRestartPolicy:
    """Restart policy configuration."""

    Name: Optional[str] = None
    MaximumRetryCount: Optional[int] = None


@dataclass
class ContainerBindOptions:
    """Bind mount options."""

    Propagation: Optional[str] = None
    NonRecursive: Optional[bool] = None
    CreateMountpoint: Optional[bool] = None
    ReadOnlyNonRecursive: Optional[bool] = None
    ReadOnlyForceRecursive: Optional[bool] = None


@dataclass
class ContainerVolumeDriverConfig:
    """Volume driver configuration."""

    Name: Optional[str] = None
    Options: Optional[dict[str, str]] = None


@dataclass
class ContainerVolumeOptions:
    """Volume mount options."""

    NoCopy: Optional[bool] = None
    Labels: Optional[dict[str, str]] = None
    DriverConfig: Optional[ContainerVolumeDriverConfig] = None
    Subpath: Optional[str] = None


@dataclass
class ContainerImageOptions:
    """Image mount options."""

    Subpath: Optional[str] = None


@dataclass
class ContainerTmpfsOptions:
    """Tmpfs mount options."""

    SizeBytes: Optional[int] = None
    Mode: Optional[int] = None
    Options: Optional[list[list[str]]] = None


@dataclass
class ContainerMountPoint:
    """Mount point configuration."""

    Target: Optional[str] = None
    Source: Optional[str] = None
    Type: Optional[str] = None
    ReadOnly: Optional[bool] = None
    Consistency: Optional[str] = None
    BindOptions: Optional[ContainerBindOptions] = None
    VolumeOptions: Optional[ContainerVolumeOptions] = None
    ImageOptions: Optional[ContainerImageOptions] = None
    TmpfsOptions: Optional[ContainerTmpfsOptions] = None


@dataclass
class ContainerHostConfig:
    """Host configuration for container."""

    CpuShares: Optional[int] = None
    Memory: Optional[int] = None
    CgroupParent: Optional[str] = None
    BlkioWeight: Optional[int] = None
    BlkioWeightDevice: Optional[list[ContainerBlkioWeightDevice]] = None
    BlkioDeviceReadBps: Optional[list[ContainerBlkioDeviceRate]] = None
    BlkioDeviceWriteBps: Optional[list[ContainerBlkioDeviceRate]] = None
    BlkioDeviceReadIOps: Optional[list[ContainerBlkioDeviceRate]] = None
    BlkioDeviceWriteIOps: Optional[list[ContainerBlkioDeviceRate]] = None
    CpuPeriod: Optional[int] = None
    CpuQuota: Optional[int] = None
    CpuRealtimePeriod: Optional[int] = None
    CpuRealtimeRuntime: Optional[int] = None
    CpusetCpus: Optional[str] = None
    CpusetMems: Optional[str] = None
    Devices: Optional[list[ContainerDeviceMapping]] = None
    DeviceCgroupRules: Optional[list[str]] = None
    DeviceRequests: Optional[list[ContainerDeviceRequest]] = None
    KernelMemoryTCP: Optional[int] = None
    MemoryReservation: Optional[int] = None
    MemorySwap: Optional[int] = None
    MemorySwappiness: Optional[int] = None
    NanoCpus: Optional[int] = None
    OomKillDisable: Optional[bool] = None
    Init: Optional[bool] = None
    PidsLimit: Optional[int] = None
    Ulimits: Optional[list[ContainerUlimit]] = None
    CpuCount: Optional[int] = None
    CpuPercent: Optional[int] = None
    IOMaximumIOps: Optional[int] = None
    IOMaximumBandwidth: Optional[int] = None
    Binds: Optional[list[str]] = None
    ContainerIDFile: Optional[str] = None
    LogConfig: Optional[ContainerLogConfig] = None
    NetworkMode: Optional[str] = None
    PortBindings: Optional[dict[str, Optional[list[ContainerPortBinding]]]] = None
    RestartPolicy: Optional[ContainerRestartPolicy] = None
    AutoRemove: Optional[bool] = None
    VolumeDriver: Optional[str] = None
    VolumesFrom: Optional[list[str]] = None
    Mounts: Optional[list[ContainerMountPoint]] = None
    ConsoleSize: Optional[list[int]] = None
    Annotations: Optional[dict[str, str]] = None
    CapAdd: Optional[list[str]] = None
    CapDrop: Optional[list[str]] = None
    CgroupnsMode: Optional[str] = None
    Dns: Optional[list[str]] = None
    DnsOptions: Optional[list[str]] = None
    DnsSearch: Optional[list[str]] = None
    ExtraHosts: Optional[list[str]] = None
    GroupAdd: Optional[list[str]] = None
    IpcMode: Optional[str] = None
    Cgroup: Optional[str] = None
    Links: Optional[list[str]] = None
    OomScoreAdj: Optional[int] = None
    PidMode: Optional[str] = None
    Privileged: Optional[bool] = None
    PublishAllPorts: Optional[bool] = None
    ReadonlyRootfs: Optional[bool] = None
    SecurityOpt: Optional[list[str]] = None
    StorageOpt: Optional[dict[str, str]] = None
    Tmpfs: Optional[dict[str, str]] = None
    UTSMode: Optional[str] = None
    UsernsMode: Optional[str] = None
    ShmSize: Optional[int] = None
    Sysctls: Optional[dict[str, str]] = None
    Runtime: Optional[str] = None
    Isolation: Optional[str] = None
    MaskedPaths: Optional[list[str]] = None
    ReadonlyPaths: Optional[list[str]] = None


@dataclass
class ContainerGraphDriver:
    """Graph driver information."""

    Name: Optional[str] = None
    Data: Optional[dict[str, str]] = None


@dataclass
class ContainerMount:
    """Mount information."""

    Type: Optional[str] = None
    Name: Optional[str] = None
    Source: Optional[str] = None
    Destination: Optional[str] = None
    Driver: Optional[str] = None
    Mode: Optional[str] = None
    RW: Optional[bool] = None
    Propagation: Optional[str] = None


@dataclass
class ContainerHealthcheck:
    """Container healthcheck configuration."""

    Test: Optional[list[str]] = None
    Interval: Optional[int] = None
    Timeout: Optional[int] = None
    Retries: Optional[int] = None
    StartPeriod: Optional[int] = None
    StartInterval: Optional[int] = None


@dataclass
class ContainerConfig:
    """Container configuration."""

    Hostname: Optional[str] = None
    Domainname: Optional[str] = None
    User: Optional[str] = None
    AttachStdin: Optional[bool] = None
    AttachStdout: Optional[bool] = None
    AttachStderr: Optional[bool] = None
    ExposedPorts: Optional[dict[str, dict[str, Any]]] = None
    Tty: Optional[bool] = None
    OpenStdin: Optional[bool] = None
    StdinOnce: Optional[bool] = None
    Env: Optional[list[str]] = None
    Cmd: Optional[list[str]] = None
    Healthcheck: Optional[ContainerHealthcheck] = None
    ArgsEscaped: Optional[bool] = None
    Image: Optional[str] = None
    Volumes: Optional[dict[str, dict[str, Any]]] = None
    WorkingDir: Optional[str] = None
    Entrypoint: Optional[list[str]] = None
    NetworkDisabled: Optional[bool] = None
    MacAddress: Optional[str] = None
    OnBuild: Optional[list[str]] = None
    Labels: Optional[dict[str, str]] = None
    StopSignal: Optional[str] = None
    StopTimeout: Optional[int] = None
    Shell: Optional[list[str]] = None


@dataclass
class ContainerIPAMConfig:
    """IPAM configuration for network."""

    IPv4Address: Optional[str] = None
    IPv6Address: Optional[str] = None
    LinkLocalIPs: Optional[list[str]] = None


@dataclass
class ContainerNetworkEndpoint:
    """Network endpoint information."""

    IPAMConfig: Optional[ContainerIPAMConfig] = None
    Links: Optional[list[str]] = None
    MacAddress: Optional[str] = None
    Aliases: Optional[list[str]] = None
    DriverOpts: Optional[dict[str, str]] = None
    GwPriority: Optional[list[int]] = None
    NetworkID: Optional[str] = None
    EndpointID: Optional[str] = None
    Gateway: Optional[str] = None
    IPAddress: Optional[str] = None
    IPPrefixLen: Optional[int] = None
    IPv6Gateway: Optional[str] = None
    GlobalIPv6Address: Optional[str] = None
    GlobalIPv6PrefixLen: Optional[int] = None
    DNSNames: Optional[list[str]] = None


@dataclass
class ContainerAddress:
    """IP address information."""

    Addr: Optional[str] = None
    PrefixLen: Optional[int] = None


@dataclass
class ContainerNetworkSettings:
    """Network settings for container."""

    Bridge: Optional[str] = None
    SandboxID: Optional[str] = None
    HairpinMode: Optional[bool] = None
    LinkLocalIPv6Address: Optional[str] = None
    LinkLocalIPv6PrefixLen: Optional[str] = None
    Ports: Optional[dict[str, Optional[list[ContainerPortBinding]]]] = None
    SandboxKey: Optional[str] = None
    SecondaryIPAddresses: Optional[list[ContainerAddress]] = None
    SecondaryIPv6Addresses: Optional[list[ContainerAddress]] = None
    EndpointID: Optional[str] = None
    Gateway: Optional[str] = None
    GlobalIPv6Address: Optional[str] = None
    GlobalIPv6PrefixLen: Optional[int] = None
    IPAddress: Optional[str] = None
    IPPrefixLen: Optional[int] = None
    IPv6Gateway: Optional[str] = None
    MacAddress: Optional[str] = None
    Networks: Optional[dict[str, ContainerNetworkEndpoint]] = None

    def get_networks(self) -> Optional[dict[str, ContainerNetworkEndpoint]]:
        """Get networks for the container."""
        return self.Networks


@dataclass
class ContainerInspectInfo:
    """Complete container information from docker inspect."""

    Id: Optional[str] = None
    Created: Optional[str] = None
    Path: Optional[str] = None
    Args: Optional[list[str]] = None
    State: Optional[ContainerState] = None
    Image: Optional[str] = None
    ResolvConfPath: Optional[str] = None
    HostnamePath: Optional[str] = None
    HostsPath: Optional[str] = None
    LogPath: Optional[str] = None
    Name: Optional[str] = None
    RestartCount: Optional[int] = None
    Driver: Optional[str] = None
    Platform: Optional[str] = None
    ImageManifestDescriptor: Optional[ContainerImageManifestDescriptor] = None
    MountLabel: Optional[str] = None
    ProcessLabel: Optional[str] = None
    AppArmorProfile: Optional[str] = None
    ExecIDs: Optional[list[str]] = None
    HostConfig: Optional[ContainerHostConfig] = None
    GraphDriver: Optional[ContainerGraphDriver] = None
    SizeRw: Optional[str] = None
    SizeRootFs: Optional[str] = None
    Mounts: Optional[list[ContainerMount]] = None
    Config: Optional[ContainerConfig] = None
    NetworkSettings: Optional[ContainerNetworkSettings] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContainerInspectInfo":
        """Create from docker inspect JSON."""
        return cls(
            Id=data.get("Id"),
            Created=data.get("Created"),
            Path=data.get("Path"),
            Args=data.get("Args"),
            State=cls._parse_state(data.get("State", {})) if data.get("State") else None,
            Image=data.get("Image"),
            ResolvConfPath=data.get("ResolvConfPath"),
            HostnamePath=data.get("HostnamePath"),
            HostsPath=data.get("HostsPath"),
            LogPath=data.get("LogPath"),
            Name=data.get("Name"),
            RestartCount=data.get("RestartCount"),
            Driver=data.get("Driver"),
            Platform=data.get("Platform"),
            ImageManifestDescriptor=cls._parse_image_manifest(data.get("ImageManifestDescriptor", {}))
            if data.get("ImageManifestDescriptor")
            else None,
            MountLabel=data.get("MountLabel"),
            ProcessLabel=data.get("ProcessLabel"),
            AppArmorProfile=data.get("AppArmorProfile"),
            ExecIDs=data.get("ExecIDs"),
            HostConfig=cls._parse_host_config(data.get("HostConfig", {})) if data.get("HostConfig") else None,
            GraphDriver=_ignore_properties(ContainerGraphDriver, data.get("GraphDriver", {}))
            if data.get("GraphDriver")
            else None,
            SizeRw=data.get("SizeRw"),
            SizeRootFs=data.get("SizeRootFs"),
            Mounts=[_ignore_properties(ContainerMount, mount) for mount in data.get("Mounts", [])],
            Config=_ignore_properties(ContainerConfig, data.get("Config", {})) if data.get("Config") else None,
            NetworkSettings=cls._parse_network_settings(data.get("NetworkSettings", {}))
            if data.get("NetworkSettings")
            else None,
        )

    @classmethod
    def _parse_state(cls, data: dict[str, Any]) -> Optional[ContainerState]:
        """Parse State with nested Health object."""
        if not data:
            return None

        health_data = data.get("Health", {})
        health = None
        if health_data:
            logs = [_ignore_properties(ContainerLog, log) for log in health_data.get("Log", [])]
            health = ContainerHealth(
                Status=health_data.get("Status"),
                FailingStreak=health_data.get("FailingStreak"),
                Log=logs if logs else None,
            )

        return ContainerState(
            Status=data.get("Status"),
            Running=data.get("Running"),
            Paused=data.get("Paused"),
            Restarting=data.get("Restarting"),
            OOMKilled=data.get("OOMKilled"),
            Dead=data.get("Dead"),
            Pid=data.get("Pid"),
            ExitCode=data.get("ExitCode"),
            Error=data.get("Error"),
            StartedAt=data.get("StartedAt"),
            FinishedAt=data.get("FinishedAt"),
            Health=health,
        )

    @classmethod
    def _parse_image_manifest(cls, data: dict[str, Any]) -> Optional[ContainerImageManifestDescriptor]:
        """Parse ImageManifestDescriptor with nested Platform."""
        if not data:
            return None

        platform_data = data.get("platform", {})
        platform = _ignore_properties(ContainerPlatform, platform_data) if platform_data else None

        return ContainerImageManifestDescriptor(
            mediaType=data.get("mediaType"),
            digest=data.get("digest"),
            size=data.get("size"),
            urls=data.get("urls"),
            annotations=data.get("annotations"),
            data=data.get("data"),
            platform=platform,
            artifactType=data.get("artifactType"),
        )

    @classmethod
    def _parse_host_config(cls, data: dict[str, Any]) -> Optional[ContainerHostConfig]:
        """Parse HostConfig with all nested objects."""
        if not data:
            return None

        blkio_weight_devices = [
            _ignore_properties(ContainerBlkioWeightDevice, d) for d in (data.get("BlkioWeightDevice") or [])
        ]
        blkio_read_bps = [
            _ignore_properties(ContainerBlkioDeviceRate, d) for d in (data.get("BlkioDeviceReadBps") or [])
        ]
        blkio_write_bps = [
            _ignore_properties(ContainerBlkioDeviceRate, d) for d in (data.get("BlkioDeviceWriteBps") or [])
        ]
        blkio_read_iops = [
            _ignore_properties(ContainerBlkioDeviceRate, d) for d in (data.get("BlkioDeviceReadIOps") or [])
        ]
        blkio_write_iops = [
            _ignore_properties(ContainerBlkioDeviceRate, d) for d in (data.get("BlkioDeviceWriteIOps") or [])
        ]
        devices = [_ignore_properties(ContainerDeviceMapping, d) for d in (data.get("Devices") or [])]
        device_requests = [_ignore_properties(ContainerDeviceRequest, d) for d in (data.get("DeviceRequests") or [])]
        ulimits = [_ignore_properties(ContainerUlimit, d) for d in (data.get("Ulimits") or [])]
        mounts = [_ignore_properties(ContainerMountPoint, d) for d in (data.get("Mounts") or [])]

        port_bindings: dict[str, Optional[list[ContainerPortBinding]]] = {}
        port_bindings_data = data.get("PortBindings")
        if port_bindings_data is not None:
            for port, bindings in port_bindings_data.items():
                if bindings is None:
                    port_bindings[port] = None
                else:
                    port_bindings[port] = [_ignore_properties(ContainerPortBinding, b) for b in bindings]

        return ContainerHostConfig(
            CpuShares=data.get("CpuShares"),
            Memory=data.get("Memory"),
            CgroupParent=data.get("CgroupParent"),
            BlkioWeight=data.get("BlkioWeight"),
            BlkioWeightDevice=blkio_weight_devices if blkio_weight_devices else None,
            BlkioDeviceReadBps=blkio_read_bps if blkio_read_bps else None,
            BlkioDeviceWriteBps=blkio_write_bps if blkio_write_bps else None,
            BlkioDeviceReadIOps=blkio_read_iops if blkio_read_iops else None,
            BlkioDeviceWriteIOps=blkio_write_iops if blkio_write_iops else None,
            CpuPeriod=data.get("CpuPeriod"),
            CpuQuota=data.get("CpuQuota"),
            CpuRealtimePeriod=data.get("CpuRealtimePeriod"),
            CpuRealtimeRuntime=data.get("CpuRealtimeRuntime"),
            CpusetCpus=data.get("CpusetCpus"),
            CpusetMems=data.get("CpusetMems"),
            Devices=devices if devices else None,
            DeviceCgroupRules=data.get("DeviceCgroupRules"),
            DeviceRequests=device_requests if device_requests else None,
            KernelMemoryTCP=data.get("KernelMemoryTCP"),
            MemoryReservation=data.get("MemoryReservation"),
            MemorySwap=data.get("MemorySwap"),
            MemorySwappiness=data.get("MemorySwappiness"),
            NanoCpus=data.get("NanoCpus"),
            OomKillDisable=data.get("OomKillDisable"),
            Init=data.get("Init"),
            PidsLimit=data.get("PidsLimit"),
            Ulimits=ulimits if ulimits else None,
            CpuCount=data.get("CpuCount"),
            CpuPercent=data.get("CpuPercent"),
            IOMaximumIOps=data.get("IOMaximumIOps"),
            IOMaximumBandwidth=data.get("IOMaximumBandwidth"),
            Binds=data.get("Binds"),
            ContainerIDFile=data.get("ContainerIDFile"),
            LogConfig=_ignore_properties(ContainerLogConfig, data.get("LogConfig", {}))
            if data.get("LogConfig")
            else None,
            NetworkMode=data.get("NetworkMode"),
            PortBindings=port_bindings if port_bindings else None,
            RestartPolicy=_ignore_properties(ContainerRestartPolicy, data.get("RestartPolicy", {}))
            if data.get("RestartPolicy")
            else None,
            AutoRemove=data.get("AutoRemove"),
            VolumeDriver=data.get("VolumeDriver"),
            VolumesFrom=data.get("VolumesFrom"),
            Mounts=mounts if mounts else None,
            ConsoleSize=data.get("ConsoleSize"),
            Annotations=data.get("Annotations"),
            CapAdd=data.get("CapAdd"),
            CapDrop=data.get("CapDrop"),
            CgroupnsMode=data.get("CgroupnsMode"),
            Dns=data.get("Dns"),
            DnsOptions=data.get("DnsOptions"),
            DnsSearch=data.get("DnsSearch"),
            ExtraHosts=data.get("ExtraHosts"),
            GroupAdd=data.get("GroupAdd"),
            IpcMode=data.get("IpcMode"),
            Cgroup=data.get("Cgroup"),
            Links=data.get("Links"),
            OomScoreAdj=data.get("OomScoreAdj"),
            PidMode=data.get("PidMode"),
            Privileged=data.get("Privileged"),
            PublishAllPorts=data.get("PublishAllPorts"),
            ReadonlyRootfs=data.get("ReadonlyRootfs"),
            SecurityOpt=data.get("SecurityOpt"),
            StorageOpt=data.get("StorageOpt"),
            Tmpfs=data.get("Tmpfs"),
            UTSMode=data.get("UTSMode"),
            UsernsMode=data.get("UsernsMode"),
            ShmSize=data.get("ShmSize"),
            Sysctls=data.get("Sysctls"),
            Runtime=data.get("Runtime"),
            Isolation=data.get("Isolation"),
            MaskedPaths=data.get("MaskedPaths"),
            ReadonlyPaths=data.get("ReadonlyPaths"),
        )

    @classmethod
    def _parse_network_settings(cls, data: dict[str, Any]) -> Optional[ContainerNetworkSettings]:
        """Parse NetworkSettings with nested Networks and Ports."""
        if not data:
            return None

        ports: dict[str, Optional[list[ContainerPortBinding]]] = {}
        ports_data = data.get("Ports")
        if ports_data is not None:
            for port, bindings in ports_data.items():
                if bindings is None:
                    ports[port] = None
                else:
                    ports[port] = [_ignore_properties(ContainerPortBinding, b) for b in bindings]

        networks = {}
        networks_data = data.get("Networks")
        if networks_data is not None:
            for name, network_data in networks_data.items():
                networks[name] = _ignore_properties(ContainerNetworkEndpoint, network_data)

        secondary_ipv4 = []
        secondary_ipv4_data = data.get("SecondaryIPAddresses")
        if secondary_ipv4_data is not None:
            secondary_ipv4 = [_ignore_properties(ContainerAddress, addr) for addr in secondary_ipv4_data]

        secondary_ipv6 = []
        secondary_ipv6_data = data.get("SecondaryIPv6Addresses")
        if secondary_ipv6_data is not None:
            secondary_ipv6 = [_ignore_properties(ContainerAddress, addr) for addr in secondary_ipv6_data]

        return ContainerNetworkSettings(
            Bridge=data.get("Bridge"),
            SandboxID=data.get("SandboxID"),
            HairpinMode=data.get("HairpinMode"),
            LinkLocalIPv6Address=data.get("LinkLocalIPv6Address"),
            LinkLocalIPv6PrefixLen=data.get("LinkLocalIPv6PrefixLen"),
            Ports=ports if ports else None,
            SandboxKey=data.get("SandboxKey"),
            SecondaryIPAddresses=secondary_ipv4 if secondary_ipv4 else None,
            SecondaryIPv6Addresses=secondary_ipv6 if secondary_ipv6 else None,
            EndpointID=data.get("EndpointID"),
            Gateway=data.get("Gateway"),
            GlobalIPv6Address=data.get("GlobalIPv6Address"),
            GlobalIPv6PrefixLen=data.get("GlobalIPv6PrefixLen"),
            IPAddress=data.get("IPAddress"),
            IPPrefixLen=data.get("IPPrefixLen"),
            IPv6Gateway=data.get("IPv6Gateway"),
            MacAddress=data.get("MacAddress"),
            Networks=networks if networks else None,
        )

    def get_network_settings(self) -> Optional[ContainerNetworkSettings]:
        """Get network settings for the container."""
        return self.NetworkSettings


def _ignore_properties(cls: type[_IPT], dict_: Any) -> _IPT:
    """omits extra fields like @JsonIgnoreProperties(ignoreUnknown = true)

    https://gist.github.com/alexanderankin/2a4549ac03554a31bef6eaaf2eaf7fd5"""
    if isinstance(dict_, cls):
        return dict_
    if not is_dataclass(cls):
        raise TypeError(f"Expected a dataclass type, got {cls}")
    class_fields = {f.name for f in fields(cls)}
    filtered = {k: v for k, v in dict_.items() if k in class_fields}
    return cast("_IPT", cls(**filtered))
