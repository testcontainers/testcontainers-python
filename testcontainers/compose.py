import subprocess

import blindspin
import requests

from testcontainers.core.waiting_utils import wait_container_is_ready
from testcontainers.core.exceptions import NoSuchPortExposed


class DockerCompose(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        with blindspin.spinner():
            subprocess.call(["docker-compose", "up", "-d"], cwd=self.filepath)

    def stop(self):
        with blindspin.spinner():
            subprocess.call(["docker-compose", "down"], cwd=self.filepath)

    def get_service_port(self, service_name, port):
        return self._get_service_info(service_name, port)[1]

    def get_service_host(self, service_name, port):
        return self._get_service_info(service_name, port)[0]

    def _get_service_info(self, service, port):
        cmd_as_list = ["docker-compose", "port", service, str(port)]
        output = subprocess.check_output(cmd_as_list,
                                         cwd=self.filepath).decode("utf-8")
        result = str(output).rstrip().split(":")
        if len(result) == 1:
            raise NoSuchPortExposed("Port {} was not exposed for service {}"
                                    .format(port, service))
        return result

    @wait_container_is_ready()
    def wait_for(self, url):
        requests.get(url)
        return self
