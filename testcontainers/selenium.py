#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Selenium containers
===================

Allows to spin up selenium containers for testing with browsers.
"""

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready

IMAGES = {
    "firefox": "selenium/standalone-firefox-debug:latest",
    "chrome": "selenium/standalone-chrome-debug:latest"
}


def get_image_name(capabilities):
    return IMAGES[capabilities['browserName']]


class BrowserWebDriverContainer(DockerContainer):
    """
    Selenium browser container for Chrome or Firefox.

    Example
    -------
    ::

        from selenium.webdriver import DesiredCapabilities

        with BrowserWebDriverContainer(DesiredCapabilities.CHROME) as chrome:
            webdriver = chrome.get_driver()
            webdriver.get("http://google.com")
            webdriver.find_element_by_name("q").send_keys("Hello")

    You can easily change browser by passing :code:`DesiredCapabilities.FIREFOX` instead.
    """
    def __init__(self, capabilities, image=None):
        self.capabilities = capabilities
        if not image:
            self.image = get_image_name(capabilities)
        self.port_to_expose = 4444
        self.vnc_port_to_expose = 5900
        super(BrowserWebDriverContainer, self).__init__(image=self.image)
        self.with_exposed_ports(self.port_to_expose, self.vnc_port_to_expose)

    def _configure(self):
        self.with_env("no_proxy", "localhost")
        self.with_env("HUB_ENV_no_proxy", "localhost")

    @wait_container_is_ready()
    def _connect(self):
        from selenium import webdriver
        return webdriver.Remote(
            command_executor=(self.get_connection_url()),
            desired_capabilities=self.capabilities)

    def get_driver(self):
        return self._connect()

    def get_connection_url(self) -> str:
        ip = self.get_container_host_ip()
        port = self.get_exposed_port(self.port_to_expose)
        return 'http://{}:{}/wd/hub'.format(ip, port)
