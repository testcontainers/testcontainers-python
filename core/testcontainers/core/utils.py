import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Final, Optional

LINUX = "linux"
MAC = "mac"
WIN = "win"


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


def os_name() -> Optional[str]:
    pl = sys.platform
    if pl == "linux" or pl == "linux2":
        return LINUX
    elif pl == "darwin":
        return MAC
    elif pl == "win32":
        return WIN
    return None


def is_mac() -> bool:
    return os_name() == MAC


def is_linux() -> bool:
    return os_name() == LINUX


def is_windows() -> bool:
    return os_name() == WIN


def is_arm() -> bool:
    return platform.machine() in ("arm64", "aarch64")


def inside_container() -> bool:
    """
    Returns true if we are running inside a container.

    https://github.com/docker/docker/blob/a9fa38b1edf30b23cae3eade0be48b3d4b1de14b/daemon/initlayer/setup_unix.go#L25
    """
    return os.path.exists("/.dockerenv")


def default_gateway_ip() -> Optional[str]:
    """
    Returns gateway IP address of the host that testcontainer process is
    running on

    https://github.com/testcontainers/testcontainers-java/blob/3ad8d80e2484864e554744a4800a81f6b7982168/core/src/main/java/org/testcontainers/dockerclient/DockerClientConfigUtils.java#L27
    """
    cmd = ["sh", "-c", "ip route|awk '/default/ { print $3 }'"]
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ip_address = process.communicate()[0]
        if ip_address and process.returncode == 0:
            return ip_address.decode("utf-8").strip().strip("\n")
        return None
    except subprocess.SubprocessError:
        return None


def raise_for_deprecated_parameter(kwargs: dict[Any, Any], name: str, replacement: str) -> dict[Any, Any]:
    """
    Raise an error if a dictionary of keyword arguments contains a key and suggest the replacement.
    """
    if kwargs.pop(name, None):
        raise ValueError(f"Use `{replacement}` instead of `{name}`")
    return kwargs


CGROUP_FILE: Final[Path] = Path("/proc/self/cgroup")


def get_running_in_container_id() -> Optional[str]:
    """
    Get the id of the currently running container
    """
    if not CGROUP_FILE.is_file():
        return None
    cgroup = CGROUP_FILE.read_text()
    for line in cgroup.splitlines(keepends=False):
        path = line.rpartition(":")[2]
        if path.startswith("/docker"):
            return path.removeprefix("/docker/")
    return None
