from dataclasses import dataclass, field
from enum import Enum
from logging import warning
from os import environ
from os.path import exists
from pathlib import Path
from typing import Optional, Union


class ConnectionMode(Enum):
    bridge_ip = "bridge_ip"
    gateway_ip = "gateway_ip"
    docker_host = "docker_host"

    @property
    def use_mapped_port(self) -> bool:
        """
        Return true if we need to use mapped port for this connection

        This is true for everything but bridge mode.
        """
        if self == self.bridge_ip:
            return False
        return True


MAX_TRIES = int(environ.get("TC_MAX_TRIES", 120))
SLEEP_TIME = int(environ.get("TC_POOLING_INTERVAL", 1))
TIMEOUT = MAX_TRIES * SLEEP_TIME

RYUK_IMAGE: str = environ.get("RYUK_CONTAINER_IMAGE", "testcontainers/ryuk:0.8.1")
RYUK_PRIVILEGED: bool = environ.get("TESTCONTAINERS_RYUK_PRIVILEGED", "false") == "true"
RYUK_DISABLED: bool = environ.get("TESTCONTAINERS_RYUK_DISABLED", "false") == "true"
RYUK_DOCKER_SOCKET: str = environ.get("TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", "/var/run/docker.sock")
RYUK_RECONNECTION_TIMEOUT: str = environ.get("RYUK_RECONNECTION_TIMEOUT", "10s")
TC_HOST_OVERRIDE: Optional[str] = environ.get("TC_HOST", environ.get("TESTCONTAINERS_HOST_OVERRIDE"))

TC_FILE = ".testcontainers.properties"
TC_GLOBAL = Path.home() / TC_FILE


def get_user_overwritten_connection_mode() -> Optional[ConnectionMode]:
    """
    Return the user overwritten connection mode.
    """
    connection_mode: str | None = environ.get("TESTCONTAINERS_CONNECTION_MODE")
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
    max_tries: int = MAX_TRIES
    sleep_time: int = SLEEP_TIME
    ryuk_image: str = RYUK_IMAGE
    ryuk_privileged: bool = RYUK_PRIVILEGED
    ryuk_disabled: bool = RYUK_DISABLED
    ryuk_docker_socket: str = RYUK_DOCKER_SOCKET
    ryuk_reconnection_timeout: str = RYUK_RECONNECTION_TIMEOUT
    tc_properties: dict[str, str] = field(default_factory=read_tc_properties)
    _docker_auth_config: Optional[str] = field(default_factory=lambda: environ.get("DOCKER_AUTH_CONFIG"))
    tc_host_override: Optional[str] = TC_HOST_OVERRIDE
    connection_mode_override: Optional[ConnectionMode] = None

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
    def timeout(self) -> int:
        return self.max_tries * self.sleep_time


testcontainers_config = TestcontainersConfiguration()

__all__ = [
    # the public API of this module
    "testcontainers_config",
    # and all the legacy things that are deprecated:
    "MAX_TRIES",
    "SLEEP_TIME",
    "TIMEOUT",
    "RYUK_IMAGE",
    "RYUK_PRIVILEGED",
    "RYUK_DISABLED",
    "RYUK_DOCKER_SOCKET",
    "RYUK_RECONNECTION_TIMEOUT",
]
