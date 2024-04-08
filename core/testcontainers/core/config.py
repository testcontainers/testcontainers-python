from dataclasses import dataclass, field
from os import environ
from os.path import exists
from pathlib import Path

MAX_TRIES = int(environ.get("TC_MAX_TRIES", 120))
SLEEP_TIME = int(environ.get("TC_POOLING_INTERVAL", 1))
TIMEOUT = MAX_TRIES * SLEEP_TIME

RYUK_IMAGE: str = environ.get("RYUK_CONTAINER_IMAGE", "testcontainers/ryuk:0.7.0")
RYUK_PRIVILEGED: bool = environ.get("TESTCONTAINERS_RYUK_PRIVILEGED", "false") == "true"
RYUK_DISABLED: bool = environ.get("TESTCONTAINERS_RYUK_DISABLED", "false") == "true"
RYUK_DOCKER_SOCKET: str = environ.get("TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", "/var/run/docker.sock")
RYUK_RECONNECTION_TIMEOUT: str = environ.get("RYUK_RECONNECTION_TIMEOUT", "10s")

TC_FILE = ".testcontainers.properties"
TC_GLOBAL = Path.home() / TC_FILE


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
        with open(file) as contents:
            tuples = [line.split("=") for line in contents.readlines() if "=" in line]
            settings = {**settings, **{item[0].strip(): item[1].strip() for item in tuples}}
    return settings


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

    def tc_properties_get_tc_host(self):
        return self.tc_properties.get("tc.host")

    @property
    def timeout(self):
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
