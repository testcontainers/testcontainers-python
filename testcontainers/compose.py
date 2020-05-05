"""
Docker compose support
======================

Allows to spin up services configured via :code:`docker-compose.yml`.
"""

import subprocess

import blindspin
import requests

from testcontainers.core.waiting_utils import wait_container_is_ready
from testcontainers.core.exceptions import NoSuchPortExposed


class DockerCompose(object):
    """
    Docker compose containers.

    Example
    -------
    ::

        with DockerCompose("/home/project", pull=True) as compose:
            host = compose.get_service_host("hub", 4444)
            port = compose.get_service_port("hub", 4444)
            driver = webdriver.Remote(
                command_executor=("http://{}:{}/wd/hub".format(host,port)),
                desired_capabilities=CHROME,
            )
            driver.get("http://automation-remarks.com")


    .. code-block:: yaml

        hub:
        image: selenium/hub
        ports:
        - "4444:4444"
        firefox:
        image: selenium/node-firefox
        links:
            - hub
        expose:
            - "5555"
        chrome:
        image: selenium/node-chrome
        links:
            - hub
        expose:
            - "5555"
    """
    def __init__(
            self,
            filepath,
            compose_file_name="docker-compose.yml",
            pull=False):
        self.filepath = filepath
        self.compose_file_name = compose_file_name
        self.pull = pull

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        with blindspin.spinner():
            if self.pull:
                subprocess.call(["docker-compose", "-f", self.compose_file_name, "pull"],
                                cwd=self.filepath)
            subprocess.call(["docker-compose", "-f", self.compose_file_name, "up", "-d"],
                            cwd=self.filepath)

    def stop(self):
        with blindspin.spinner():
            subprocess.call(["docker-compose", "-f", self.compose_file_name, "down", "-v"],
                            cwd=self.filepath)

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
