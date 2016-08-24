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
    hub_port = 4444
    vnc_port = 5900

    def __init__(self, browser, version):
        super(GenericSeleniumContainer, self).__init__()
        self._capabilities = DesiredCapabilities.FIREFOX
        self._driver = None
        self._version = version
        self._browser = browser

    @wait_container_is_ready()
    def _connect(self):
        self._driver = webdriver.Remote(
            command_executor=('http://{}:{}/wd/hub'.format(
                self._host, self.hub_port)),
            desired_capabilities=self._capabilities)

    def _set_capabilities(self, capabilities):
        self._capabilities = capabilities

    def get_driver(self):
        return self._driver

    def _configure(self):
        pass

    def start(self):
        pass


class StandaloneSeleniumContainer(GenericSeleniumContainer):
    standalone_firefox = "selenium/standalone-firefox-debug"
    standalone_chrome = "selenium/standalone-chrome-debug"

    def __init__(self, image_for="firefox", version="latest"):
        super(StandaloneSeleniumContainer, self).__init__(image_for, version)

    def _configure(self):
        self.bind_ports(self.hub_port, self.hub_port)
        self.bind_ports(self.vnc_port, self.vnc_port)
        if self._browser.__contains__("chrome"):
            self._set_capabilities(DesiredCapabilities.CHROME)

    def start(self):
        self._configure()
        self._docker.run(image=self._get_image, bind_ports=self._exposed_ports)
        self._connect()
        return self

    @property
    def _get_image(self):
        self._image_name = self.standalone_firefox
        if self._capabilities["browserName"] == "chrome":
            self._image_name = self.standalone_chrome
        return "{}:{}".format(self._image_name, self._version)


class SeleniumHubContainer(DockerContainer):
    name = "selenium-hub"
    host = "localhost"
    default_port = 4444

    def __init__(self, capabilities, version):
        super(SeleniumHubContainer, self).__init__()
        self._image_name = "selenium/hub"
        self._version = version
        self._capabilities = capabilities
        self.driver = None

    def _configure(self):
        self.bind_ports(self.default_port, self.default_port)

    def start(self):
        self._configure()
        return self._docker.run(image=self._get_image, bind_ports=self._exposed_ports, name=self.name)

    @wait_container_is_ready()
    def _connect(self):
        self.driver = webdriver.Remote(
            command_executor=('http://{}:{}/wd/hub'.format(
                self.host, self.default_port)),
            desired_capabilities=self._capabilities)


class FireFoxContainer(DockerContainer):
    name = "firefox-node"
    default_port = 5900

    def __init__(self, version):
        super(FireFoxContainer, self).__init__()
        self._version = version
        self._image_name = "selenium/node-firefox-debug"
        self.vnc_port = 5900

    def start(self):
        self._configure()
        return self._docker.run(image=self._get_image,
                                bind_ports=self._exposed_ports,
                                env=self._env,
                                links=self._links,
                                name=self.name)

    def _connect(self):
        pass

    def _configure(self):
        self.bind_ports(self.default_port, self.vnc_port)
        self.add_env("no_proxy", "localhost")
        self.add_env("HUB_ENV_no_proxy", "localhost")
        self.link_containers(SeleniumHubContainer.name, "hub")


class ChromeContainer(DockerContainer):
    name = "chrome-node"
    default_port = 5900

    def __init__(self, version):
        super(ChromeContainer, self).__init__()
        self._version = version
        self._image_name = "selenium/node-chrome-debug"
        self.vnc_port = 5900

    def start(self):
        self._configure()
        return self._docker.run(image=self._get_image,
                                bind_ports=self._exposed_ports,
                                env=self._env,
                                links=self._links,
                                name=self.name)

    def _connect(self):
        pass

    def _configure(self):
        self.bind_ports(self.default_port, self.vnc_port)
        self.add_env("no_proxy", "localhost")
        self.add_env("HUB_ENV_no_proxy", "localhost")
        self.link_containers(SeleniumHubContainer.name, "hub")


class BrowserWebDriverContainer(DockerContainer):
    def __init__(self, capabilities=DesiredCapabilities.FIREFOX, version="latest"):
        super(BrowserWebDriverContainer, self).__init__()
        self._capabilities = capabilities
        self._version = version
        self.hub = SeleniumHubContainer(self._capabilities, self._version)
        self._spawned = []

    def start(self):
        """
        Start selenium containers and wait until they are ready
        :return:
        """
        hub_container = self.hub.start()
        self._add_to_spawn(hub_container)
        if self._capabilities["browserName"] == "firefox":
            ff = FireFoxContainer(self._version).start()
            self._add_to_spawn(ff)
        else:
            chrome = ChromeContainer(self._version).start()
            self._add_to_spawn(chrome)
        self.hub._connect()
        return self

    def _configure(self):
        pass

    def _connect(self):
        pass

    def _add_to_spawn(self, container):
        self._docker._containers.append(container)

    def get_driver(self):
        return self.hub.driver
