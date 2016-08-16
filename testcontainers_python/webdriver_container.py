from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import context_manager
from testcontainers_python import config
from testcontainers_python.docker_client import DockerClient


class WebDriverContainer(object):
    def __init__(self, capabilities=DesiredCapabilities.FIREFOX):
        self._docker = DockerClient()
        self._capabilities = capabilities
        self._driver = None
        self._containers = []

    def __enter__(self):
        return self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        """
        Start selenium containers and wait until they are ready
        :return:
        """
        hub = self._docker.run(**config.hub)
        if self._capabilities["browserName"] == "firefox":
            self._containers.append(self._docker.run(**config.firefox_node))
        else:
            self._containers.append(self._docker.run(**config.chrome_node))
        self._driver = self._connect(hub, 4444)
        self._containers.append(hub)
        return self

    @context_manager.wait_container_is_ready()
    def _connect(self, container, port):
        hub_info = self._docker.port(container, port)[0]
        return webdriver.Remote(
            command_executor='http://{}:4444/wd/hub'.format(hub_info['HostIp']),
            desired_capabilities=self._capabilities)

    def stop(self):
        """
        Stop all spawned containers
        :return:
        """
        for cont in self._containers:
            self._docker.remove(cont, True)

    def get_driver(self):
        return self._driver
