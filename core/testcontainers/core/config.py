import types
import warnings
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from logging import warning
from os import environ
from os.path import exists
from pathlib import Path
from typing import Final, Optional, Union

import docker

ENABLE_FLAGS = ("yes", "true", "t", "y", "1")


class ConnectionMode(Enum):
    bridge_ip = "bridge_ip"
    gateway_ip = "gateway_ip"
    docker_host = "docker_host"

    @property
    def use_mapped_port(self) -> bool:
        """
        Return True if mapped ports should be used for this connection mode.

        Mapped ports are used for all connection modes except 'bridge_ip'.
        """
        return self != ConnectionMode.bridge_ip


def get_docker_socket() -> str:
    """
    Determine the docker socket, prefer value given by env variable

    Using the docker api ensure we handle rootless docker properly
    """
    if socket_path := environ.get("TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", ""):
        return socket_path

    try:
        client = docker.from_env()
        socket_path = client.api.get_adapter(client.api.base_url).socket_path
        # return the normalized path as string
        return str(Path(socket_path).absolute())
    except Exception:
        return "/var/run/docker.sock"


TC_FILE = ".testcontainers.properties"
TC_GLOBAL = Path.home() / TC_FILE


def get_user_overwritten_connection_mode() -> Optional[ConnectionMode]:
    """
    Return the user overwritten connection mode.
    """
    connection_mode: Union[str, None] = environ.get("TESTCONTAINERS_CONNECTION_MODE")
    if connection_mode:
        try:
            return ConnectionMode(connection_mode)
        except ValueError as e:
            raise ValueError(f"Error parsing TESTCONTAINERS_CONNECTION_MODE: {e}") from e
    return None


def read_tc_properties() -> dict[str, str]:
    """
    Read the .testcontainers.properties for settings. (see the Java implementation for details)
    Currently we only support the ~/.testcontainers.properties but may extend to per-project variables later.

    :return: the merged properties from the sources.
    """
    tc_files = [item for item in [TC_GLOBAL] if exists(item)]
    if not tc_files:
        return {}
    settings: dict[str, str] = {}

    for file in tc_files:
        with open(file) as contents:
            tuples = [line.split("=") for line in contents.readlines() if "=" in line]
            settings = {**settings, **{item[0].strip(): item[1].strip() for item in tuples}}
    return settings


_WARNINGS = {"DOCKER_AUTH_CONFIG": "DOCKER_AUTH_CONFIG is experimental, see testcontainers/testcontainers-python#566"}


@dataclass
class TestcontainersConfiguration:
    def _render_bool(self, env_name: str, prop_name: str) -> bool:
        env_val = environ.get(env_name, None)
        if env_val is not None:
            return env_val.lower() in ENABLE_FLAGS
        prop_val = self.tc_properties.get(prop_name, None)
        if prop_val is not None:
            return prop_val.lower() in ENABLE_FLAGS
        return False

    max_tries: int = int(environ.get("TC_MAX_TRIES", "120"))
    sleep_time: float = float(environ.get("TC_POOLING_INTERVAL", "1"))
    ryuk_image: str = environ.get("RYUK_CONTAINER_IMAGE", "testcontainers/ryuk:0.8.1")
    _ryuk_privileged: Optional[bool] = None
    _ryuk_disabled: Optional[bool] = None
    _ryuk_docker_socket: str = ""
    ryuk_reconnection_timeout: str = environ.get("RYUK_RECONNECTION_TIMEOUT", "10s")
    tc_properties: dict[str, str] = field(default_factory=read_tc_properties)
    _docker_auth_config: Optional[str] = field(default_factory=lambda: environ.get("DOCKER_AUTH_CONFIG"))
    tc_host_override: Optional[str] = environ.get("TC_HOST", environ.get("TESTCONTAINERS_HOST_OVERRIDE"))
    connection_mode_override: Optional[ConnectionMode] = field(default_factory=get_user_overwritten_connection_mode)

    """
    https://github.com/testcontainers/testcontainers-go/blob/dd76d1e39c654433a3d80429690d07abcec04424/docker.go#L644
    if os env TC_HOST is set, use it
    """

    @property
    def docker_auth_config(self) -> Optional[str]:
        config = self._docker_auth_config
        if config and "DOCKER_AUTH_CONFIG" in _WARNINGS:
            warning(_WARNINGS.pop("DOCKER_AUTH_CONFIG"))
        return config

    @docker_auth_config.setter
    def docker_auth_config(self, value: str) -> None:
        if "DOCKER_AUTH_CONFIG" in _WARNINGS:
            warning(_WARNINGS.pop("DOCKER_AUTH_CONFIG"))
        self._docker_auth_config = value

    def tc_properties_get_tc_host(self) -> Union[str, None]:
        return self.tc_properties.get("tc.host")

    @property
    def ryuk_privileged(self) -> bool:
        if self._ryuk_privileged is not None:
            return bool(self._ryuk_privileged)
        self._ryuk_privileged = self._render_bool("TESTCONTAINERS_RYUK_PRIVILEGED", "ryuk.container.privileged")
        return self._ryuk_privileged

    @ryuk_privileged.setter
    def ryuk_privileged(self, value: bool) -> None:
        self._ryuk_privileged = value

    @property
    def ryuk_disabled(self) -> bool:
        if self._ryuk_disabled is not None:
            return bool(self._ryuk_disabled)
        self._ryuk_disabled = self._render_bool("TESTCONTAINERS_RYUK_DISABLED", "ryuk.disabled")
        return self._ryuk_disabled

    @ryuk_disabled.setter
    def ryuk_disabled(self, value: bool) -> None:
        self._ryuk_disabled = value

    @property
    def timeout(self) -> float:
        return self.max_tries * self.sleep_time

    @property
    def ryuk_docker_socket(self) -> str:
        if not self._ryuk_docker_socket:
            self.ryuk_docker_socket = get_docker_socket()
        return self._ryuk_docker_socket

    @ryuk_docker_socket.setter
    def ryuk_docker_socket(self, value: str) -> None:
        self._ryuk_docker_socket = value


testcontainers_config: Final = TestcontainersConfiguration()

__all__ = [
    # Public API of this module:
    "ConnectionMode",
    "testcontainers_config",
]

_deprecated_attribute_mapping: Final[Mapping[str, str]] = types.MappingProxyType(
    {
        "MAX_TRIES": "max_tries",
        "RYUK_DISABLED": "ryuk_disabled",
        "RYUK_DOCKER_SOCKET": "ryuk_docker_socket",
        "RYUK_IMAGE": "ryuk_image",
        "RYUK_PRIVILEGED": "ryuk_privileged",
        "RYUK_RECONNECTION_TIMEOUT": "ryuk_reconnection_timeout",
        "SLEEP_TIME": "sleep_time",
        "TIMEOUT": "timeout",
    }
)


def __dir__() -> list[str]:
    return __all__ + list(_deprecated_attribute_mapping.keys())


def __getattr__(name: str) -> object:
    """
    Allow getting deprecated legacy settings.
    """
    module = f"{__name__!r}"

    if name in _deprecated_attribute_mapping:
        attrib = _deprecated_attribute_mapping[name]
        warnings.warn(
            f"{module}.{name} is deprecated. Use {module}.testcontainers_config.{attrib} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(testcontainers_config, attrib)
    raise AttributeError(f"module {module} has no attribute {name!r}")
