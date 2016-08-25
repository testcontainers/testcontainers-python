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

from testcontainers.config import SeleniumConfig
from testcontainers.generic import DockerContainer
from testcontainers.waiting_utils import wait_container_is_ready


class GenericSeleniumContainer(DockerContainer):
    def __init__(self, config):
        super(GenericSeleniumContainer, self).__init__(config)

    @wait_container_is_ready()
    def _connect(self):
        self._driver = webdriver.Remote(
            command_executor=('http://{}:{}/wd/hub'.format(
                self.config.host_ip, self.config.hub_container_port)),
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
    def __init__(self, config):
        super(SeleniumGridContainers, self).__init__(config)

    def start(self):
        self._start_nub()
        self._start_node()
        self._connect()
        return self

    def _start_nub(self):
        hub_image_name = "{}:{}".format(SeleniumConfig.hub_image, self.config.version)
        return self._docker.run(image=hub_image_name,
                                bind_ports={self.config.hub_host_port: self.config.hub_container_port},
                                name=self.config.hub_container_name)

    def _start_node(self):
        return self._docker.run(image=self._get_image,
                                bind_ports={self.config.vnc_host_port: self.config.vnc_container_port},
                                env=self.config.env,
                                links={self.config.hub_container_name: "hub"})

    @property
    def _get_image(self):
        self.config._image_name = SeleniumConfig.firefox_node_image
        if self.config.capabilities["browserName"] == "chrome":
            self.config._image_name = SeleniumConfig.chrome_node_image
        return self.config.image
