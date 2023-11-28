import os
import platform
import sys
import subprocess
import logging

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


def os_name() -> str:
    pl = sys.platform
    if pl == "linux" or pl == "linux2":
        return LINUX
    elif pl == "darwin":
        return MAC
    elif pl == "win32":
        return WIN


def is_mac() -> bool:
    return MAC == os_name()


def is_linux() -> bool:
    return LINUX == os_name()


def is_windows() -> bool:
    return WIN == os_name()


def is_arm() -> bool:
    return platform.machine() in ('arm64', 'aarch64')


def inside_container() -> bool:
    """
    Returns true if we are running inside a container.

    https://github.com/docker/docker/blob/a9fa38b1edf30b23cae3eade0be48b3d4b1de14b/daemon/initlayer/setup_unix.go#L25
    """
    return os.path.exists('/.dockerenv')


def default_gateway_ip() -> str:
    """
    Returns gateway IP address of the host that testcontainer process is
    running on

    https://github.com/testcontainers/testcontainers-java/blob/3ad8d80e2484864e554744a4800a81f6b7982168/core/src/main/java/org/testcontainers/dockerclient/DockerClientConfigUtils.java#L27
    """
    cmd = ["sh", "-c", "ip route|awk '/default/ { print $3 }'"]
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        ip_address = process.communicate()[0]
        if ip_address and process.returncode == 0:
            return ip_address.decode('utf-8').strip().strip('\n')
    except subprocess.SubprocessError:
        return None


def raise_for_deprecated_parameter(kwargs: dict, name: str, replacement: str) -> dict:
    """
    Raise an error if a dictionary of keyword arguments contains a key and suggest the replacement.
    """
    if kwargs.pop(name, None):
        raise ValueError(f"Use `{replacement}` instead of `{name}`")
    return kwargs
