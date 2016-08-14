import logging
from time import sleep

from testcontainers_python import config
from testcontainers_python.docker_client import DockerClient
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class WebDriverContainer(object):
    def __init__(self):
        self._docker = DockerClient()
        self.capabilities = DesiredCapabilities.FIREFOX
        self._driver = None

    def with_desired_capabilities(self, capabilities):
        self.capabilities = capabilities
        return self

    def start(self):
        self._docker.run('selenium/hub:2.53.0', bind_ports={4444: 4444}, name='selenium-hub')
        if self.capabilities["browserName"] == "firefox":
            self._docker.run('selenium/node-firefox:2.53.0', links={'selenium-hub': 'hub'})
        else:
            self._docker.run('selenium/node-chrome:2.53.0', links={'selenium-hub': 'hub'})
        self._driver = self._wait_for_container_to_start()
        return self

    def _wait_for_container_to_start(self):
        for _ in range(0, config.max_tries):
            try:
                return webdriver.Remote(
                    command_executor='http://127.0.0.1:4444/wd/hub',
                    desired_capabilities=self.capabilities)
            except Exception:
                logging.warning("Waiting for container to start")
                sleep(config.sleep_time)
        raise Exception()

    def get_driver(self):
        return self._driver
