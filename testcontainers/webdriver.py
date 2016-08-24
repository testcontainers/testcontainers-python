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
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from testcontainers.generic import DockerContainer
from testcontainers.waiting_utils import wait_container_is_ready


class GenericSeleniumContainer(DockerContainer):
    def __init__(self, config):
        super(GenericSeleniumContainer, self).__init__(config)

    @wait_container_is_ready()
    def _connect(self):
        self._driver = webdriver.Remote(
            command_executor=('http://{}:{}/wd/hub'.format(
                self.config.host_ip, self.config.hub_port)),
            desired_capabilities=self.config.capabilities)

    def get_driver(self):
        return self._driver

    def start(self):
        raise NotImplementedError


class StandaloneSeleniumContainer(GenericSeleniumContainer):
    def __init__(self, config):
        super(StandaloneSeleniumContainer, self).__init__(config)

    def start(self):
        self._docker.run(image=self._get_image, bind_ports=self.config.port_bindings)
        self._connect()
        return self

    @property
    def _get_image(self):
        self.config._image_name = self.config.standalone_firefox
        if self.config.capabilities["browserName"] == "chrome":
            self.config._image_name = self.config.standalone_chrome
        return self.config.image


class SeleniumGridContainers(GenericSeleniumContainer):
    hub_image = "selenium/hub"
    firefox_node_image = "selenium/node-firefox-debug"
    chrome_node_image = "selenium/node-chrome-debug"
    host_hub_port = 4444
    hub_container_name = "selenium-hub"

    def __init__(self, image_for="firefox", version="latest"):
        super(SeleniumGridContainers, self).__init__(image_for, version)

    def _configure(self):
        if self._browser.__contains__("chrome"):
            self._set_capabilities(DesiredCapabilities.CHROME)
        self.add_env("no_proxy", "localhost")
        self.add_env("HUB_ENV_no_proxy", "localhost")
        self.link_containers(SeleniumGridContainers.hub_container_name, "hub")
        self.bind_ports(self.host_vnc_port, self.container_vnc_port)

    def start(self):
        self._configure()
        self._start_nub()
        self._start_node()
        self._connect()
        return self

    def _start_nub(self):
        image_name = "{}:{}".format(self.hub_image, self._version)
        return self._docker.run(image=image_name, bind_ports={self.hub_port: self.host_hub_port},
                                name=self.hub_container_name)

    def _start_node(self):
        return self._docker.run(image=self._get_image,
                                bind_ports=self._binded_ports,
                                env=self._env,
                                links=self._links)

    @property
    def _get_image(self):
        self._image_name = self.firefox_node_image
        if self._capabilities["browserName"] == "chrome":
            self._image_name = self.chrome_node_image
        return "{}:{}".format(self._image_name, self._version)
