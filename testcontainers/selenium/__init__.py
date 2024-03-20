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

from typing import Optional

import urllib3

from selenium import webdriver
from selenium.webdriver.common.options import ArgOptions
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready

IMAGES = {"firefox": "selenium/standalone-firefox-debug:latest", "chrome": "selenium/standalone-chrome-debug:latest"}


def get_image_name(capabilities: str) -> str:
    return IMAGES[capabilities["browserName"]]


class BrowserWebDriverContainer(DockerContainer):
    """
    Selenium browser container for Chrome or Firefox.

    Example:

        .. doctest::

            >>> from testcontainers.selenium import BrowserWebDriverContainer
            >>> from selenium.webdriver import DesiredCapabilities

            >>> with BrowserWebDriverContainer(DesiredCapabilities.CHROME) as chrome:
            ...    webdriver = chrome.get_driver()

        You can easily change browser by passing :code:`DesiredCapabilities.FIREFOX` instead.
    """

    def __init__(
        self, capabilities: str, image: Optional[str] = None, port: int = 4444, vnc_port: int = 5900, **kwargs
    ) -> None:
        self.capabilities = capabilities
        self.image = image or get_image_name(capabilities)
        self.port = port
        self.vnc_port = vnc_port
        super().__init__(image=self.image, **kwargs)
        self.with_exposed_ports(self.port, self.vnc_port)

    def _configure(self) -> None:
        self.with_env("no_proxy", "localhost")
        self.with_env("HUB_ENV_no_proxy", "localhost")

    @wait_container_is_ready(urllib3.exceptions.HTTPError)
    def _connect(self) -> webdriver.Remote:
        options = ArgOptions()
        for key, value in self.capabilities.items():
            options.set_capability(key, value)
        return webdriver.Remote(command_executor=(self.get_connection_url()), options=options)

    def get_driver(self) -> webdriver.Remote:
        return self._connect()

    def get_connection_url(self) -> str:
        ip = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"http://{ip}:{port}/wd/hub"
