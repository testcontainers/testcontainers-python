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
import uuid
from pathlib import Path
from typing import Optional

import urllib3
from selenium import webdriver
from selenium.webdriver.common.options import ArgOptions
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready

from .video import SeleniumVideoContainer

EMPTY_PATH = "."

IMAGES = {
    "firefox": "selenium/standalone-firefox:4.13.0-20231004",
    "chrome": "selenium/standalone-chrome:4.13.0-20231004"
}


def get_image_name(capabilities: str) -> str:
    return IMAGES[capabilities['browserName']]


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

    def __init__(self, capabilities: str, image: Optional[str] = None, port: int = 4444,
                 vnc_port: int = 5900, **kwargs) -> None:
        self.capabilities = capabilities
        self.image = image or get_image_name(capabilities)
        self.port = port
        self.vnc_port = vnc_port
        super(BrowserWebDriverContainer, self).__init__(image=self.image, **kwargs)
        self.with_exposed_ports(self.port, self.vnc_port)
        self.video = None
        self.network = None

    def _configure(self) -> None:
        self.with_env("no_proxy", "localhost")
        self.with_env("HUB_ENV_no_proxy", "localhost")

    @wait_container_is_ready(urllib3.exceptions.HTTPError)
    def _connect(self) -> webdriver.Remote:
        options = ArgOptions()
        for key, value in self.capabilities.items():
            options.set_capability(key, value)
        return webdriver.Remote(
            command_executor=(self.get_connection_url()),
            options=options)

    def get_driver(self) -> webdriver.Remote:
        return self._connect()

    def get_connection_url(self) -> str:
        ip = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f'http://{ip}:{port}/wd/hub'

    def with_video(self, video_path: Path = Path.cwd()) -> 'DockerContainer':
        self.video = SeleniumVideoContainer()

        target_video_path = video_path.parent
        if target_video_path.samefile(EMPTY_PATH):
            target_video_path = Path.cwd()
        self.video.save_videos(str(target_video_path))

        if video_path.name:
            self.video.set_video_name(video_path.name)

        return self

    def start(self) -> 'DockerContainer':
        if self.video:
            self.network = self._docker.client.networks.create(str(uuid.uuid1()))
            self.set_network_name(self.network.name)
            self.video.set_network_name(self.network.name)

            super().start()

            self.video.set_selenium_container_host(self.get_wrapped_container().short_id)
            self.video.start()

            return self

        super().start()
        return self

    def stop(self, force=True, delete_volume=True) -> None:
        if self.video:
            # Video need to stop before remove
            self.video.get_wrapped_container().stop()
            self.video.stop(force, delete_volume)

        super().stop(force, delete_volume)

        if self.network:
            self.get_docker_client().client.api.remove_network(self.network.id)
