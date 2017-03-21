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
