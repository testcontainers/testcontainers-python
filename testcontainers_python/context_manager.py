import logging
from time import sleep

import wrapt

from testcontainers_python import config
from testcontainers_python.brogress_bar import ConsoleProgressBar
from testcontainers_python.docker_client import DockerClient
from testcontainers_python.exceptions import TimeoutException


class docker_client(object):
    def __init__(self, base_url=config.docker_base_url):
        self._docker = DockerClient(base_url)

    def __enter__(self):
        return self._docker

    def __exit__(self, type, value, traceback):
        for cont in self._docker.get_containers():
            self._docker.stop(cont)
            self._docker.remove(cont, True)


def wait_container_is_ready():
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        bar = ConsoleProgressBar().bar
        logging.warning("Waiting for container to start")
        for _ in bar(range(0, config.max_tries)):
            try:
                return wrapped(*args, **kwargs)
            except Exception:
                sleep(config.sleep_time)
        raise TimeoutException("Wait time exceeded {} sec.".format(config.max_tries))
    return wrapper
