import os
import sys

LINUX = "linux"
MAC = "mac"
WIN = "win"


def os_name():
    pl = sys.platform
    if pl == "linux" or pl == "linux2":
        return LINUX
    elif pl == "darwin":
        return MAC
    elif pl == "win32":
        return WIN


def is_mac():
    return MAC == os_name()


def is_linux():
    return LINUX == os_name()


def is_windows():
    return WIN == os_name()


def inside_container():
    """
    Returns true if we are running inside a container.

    https://github.com/docker/docker/blob/a9fa38b1edf30b23cae3eade0be48b3d4b1de14b/daemon/initlayer/setup_unix.go#L25
    """
    return os.path.exists('/.dockerenv')
