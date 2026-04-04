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

"""Docker Engine API data structures for container inspect responses."""

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Optional, TypeVar

_IPT = TypeVar("_IPT")


def _ignore_properties(cls: type[_IPT], dict_: Any) -> _IPT:
    """omits extra fields like @JsonIgnoreProperties(ignoreUnknown = true)

    https://gist.github.com/alexanderankin/2a4549ac03554a31bef6eaaf2eaf7fd5"""
    if isinstance(dict_, cls):
        return dict_
    if not is_dataclass(cls):
        raise TypeError(f"Expected a dataclass type, got {cls}")
    class_fields = {f.name for f in fields(cls)}
    filtered = {k: v for k, v in dict_.items() if k in class_fields}
    return cls(**filtered)


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

    def __post_init__(self) -> None:
        list_conversions = [
            ("BlkioWeightDevice", ContainerBlkioWeightDevice),
            ("BlkioDeviceReadBps", ContainerBlkioDeviceRate),
            ("BlkioDeviceWriteBps", ContainerBlkioDeviceRate),
            ("BlkioDeviceReadIOps", ContainerBlkioDeviceRate),
            ("BlkioDeviceWriteIOps", ContainerBlkioDeviceRate),
            ("Devices", ContainerDeviceMapping),
            ("DeviceRequests", ContainerDeviceRequest),
            ("Ulimits", ContainerUlimit),
            ("Mounts", ContainerMountPoint),
        ]

        for field_name, target_class in list_conversions:
            field_value = getattr(self, field_name)
            if field_value is not None and isinstance(field_value, list):
                setattr(
                    self,
                    field_name,
                    [
                        _ignore_properties(target_class, item) if isinstance(item, dict) else item
                        for item in field_value
                    ],
                )

        if self.LogConfig is not None and isinstance(self.LogConfig, dict):
            self.LogConfig = _ignore_properties(ContainerLogConfig, self.LogConfig)

        if self.RestartPolicy is not None and isinstance(self.RestartPolicy, dict):
            self.RestartPolicy = _ignore_properties(ContainerRestartPolicy, self.RestartPolicy)

        if self.PortBindings is not None and isinstance(self.PortBindings, dict):
            for port, bindings in self.PortBindings.items():
                if bindings is not None and isinstance(bindings, list):
                    self.PortBindings[port] = [
                        _ignore_properties(ContainerPortBinding, b) if isinstance(b, dict) else b for b in bindings
                    ]


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

    def __post_init__(self) -> None:
        if self.Ports is not None and isinstance(self.Ports, dict):
            for port, bindings in self.Ports.items():
                if bindings is not None and isinstance(bindings, list):
                    self.Ports[port] = [
                        _ignore_properties(ContainerPortBinding, b) if isinstance(b, dict) else b for b in bindings
                    ]

        if self.Networks is not None and isinstance(self.Networks, dict):
            for name, network_data in self.Networks.items():
                if isinstance(network_data, dict):
                    self.Networks[name] = _ignore_properties(ContainerNetworkEndpoint, network_data)

        if self.SecondaryIPAddresses is not None and isinstance(self.SecondaryIPAddresses, list):
            self.SecondaryIPAddresses = [
                _ignore_properties(ContainerAddress, addr) if isinstance(addr, dict) else addr
                for addr in self.SecondaryIPAddresses
            ]

        if self.SecondaryIPv6Addresses is not None and isinstance(self.SecondaryIPv6Addresses, list):
            self.SecondaryIPv6Addresses = [
                _ignore_properties(ContainerAddress, addr) if isinstance(addr, dict) else addr
                for addr in self.SecondaryIPv6Addresses
            ]

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
            HostConfig=_ignore_properties(ContainerHostConfig, data.get("HostConfig", {}))
            if data.get("HostConfig")
            else None,
            GraphDriver=_ignore_properties(ContainerGraphDriver, data.get("GraphDriver", {}))
            if data.get("GraphDriver")
            else None,
            SizeRw=data.get("SizeRw"),
            SizeRootFs=data.get("SizeRootFs"),
            Mounts=[_ignore_properties(ContainerMount, mount) for mount in data.get("Mounts", [])],
            Config=_ignore_properties(ContainerConfig, data.get("Config", {})) if data.get("Config") else None,
            NetworkSettings=_ignore_properties(ContainerNetworkSettings, data.get("NetworkSettings", {}))
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
        return _ignore_properties(ContainerHostConfig, data)

    @classmethod
    def _parse_network_settings(cls, data: dict[str, Any]) -> Optional[ContainerNetworkSettings]:
        """Parse NetworkSettings with nested Networks and Ports."""
        if not data:
            return None
        return _ignore_properties(ContainerNetworkSettings, data)

    def get_network_settings(self) -> Optional[ContainerNetworkSettings]:
        """Get network settings for the container."""
        return self.NetworkSettings
