from dataclasses import dataclass
from os import environ

MAX_TRIES = int(environ.get("TC_MAX_TRIES", 120))
SLEEP_TIME = int(environ.get("TC_POOLING_INTERVAL", 1))
TIMEOUT = MAX_TRIES * SLEEP_TIME

RYUK_IMAGE: str = environ.get("RYUK_CONTAINER_IMAGE", "testcontainers/ryuk:0.7.0")
RYUK_PRIVILEGED: bool = environ.get("TESTCONTAINERS_RYUK_PRIVILEGED", "false") == "true"
RYUK_DISABLED: bool = environ.get("TESTCONTAINERS_RYUK_DISABLED", "false") == "true"
RYUK_DOCKER_SOCKET: str = environ.get("TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", "/var/run/docker.sock")
RYUK_RECONNECTION_TIMEOUT: str = environ.get("RYUK_RECONNECTION_TIMEOUT", "10s")


@dataclass
class TestcontainersConfiguration:
    max_tries: int = MAX_TRIES
    sleep_time: int = SLEEP_TIME
    ryuk_image: str = RYUK_IMAGE
    ryuk_privileged: bool = RYUK_PRIVILEGED
    ryuk_disabled: bool = RYUK_DISABLED
    ryuk_docker_socket: str = RYUK_DOCKER_SOCKET
    ryuk_reconnection_timeout: str = RYUK_RECONNECTION_TIMEOUT

    @property
    def timeout(self):
        return self.max_tries * self.sleep_time


testcontainers_config = TestcontainersConfiguration()

__all__ = ["testcontainers_config"]
