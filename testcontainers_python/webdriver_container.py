from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from testcontainers_python import config
from testcontainers_python.generic_container import GenericContainer
from testcontainers_python.waiting_utils import wait_container_is_ready


class WebDriverContainer(GenericContainer):
    def __init__(self, capabilities=DesiredCapabilities.FIREFOX):
        GenericContainer.__init__(self)
        self._capabilities = capabilities
        self.driver = None

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
        self.driver = self._connect(hub, 4444)
        self._containers.append(hub)
        return self

    @wait_container_is_ready()
    def _connect(self, container, port):
        hub_info = self._docker.port(container, port)[0]
        return webdriver.Remote(
            command_executor='http://{}:4444/wd/hub'.format(hub_info['HostIp']),
            desired_capabilities=self._capabilities)
