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

from testcontainers.config import ContainerConfig
from testcontainers.generic import GenericSeleniumContainer


class StandaloneSeleniumContainer(GenericSeleniumContainer):
    def __init__(self, config):
        super(StandaloneSeleniumContainer, self).__init__(config)

    def start(self):
        self._docker.run(image=self.config.image,
                         bind_ports=self.config.port_bindings,
                         env=self.config.env,
                         links=self.config.container_links,
                         name=self.config.name)
        return self


class StandaloneSeleniumConfig(ContainerConfig):
    FIREFOX = "selenium/standalone-firefox-debug"
    CHROME = "selenium/standalone-chrome-debug"

    def __init__(self, image, capabilities, version="latest", name=None, host_port=4444, container_port=4444,
                 host_vnc_port=5900, container_vnc_port=5900):
        super(StandaloneSeleniumConfig, self).__init__(image=image, version=version)
        self.host_port = host_port
        self.capabilities = capabilities
        self.name = name
        if host_port:
            self.bind_ports(host_port, container_port)
        self.bind_ports(host_vnc_port, container_vnc_port)
        self.add_env("no_proxy", "localhost")  # this is workaround due to bug in Selenium images
        self.add_env("HUB_ENV_no_proxy", "localhost")


class NodeConfig(ContainerConfig):
    def __init__(self, image, version="latest", link_name="selenium-hub",
                 host_vnc_port=5900, container_vnc_port=5900, name=None):
        super(NodeConfig, self).__init__(image=image, version=version)
        self.name = name
        self.bind_ports(host_vnc_port, container_vnc_port)
        self.link_containers(link_name, "hub")
        self.add_env("no_proxy", "localhost")  # this is workaround due to bug in Selenium images
        self.add_env("HUB_ENV_no_proxy", "localhost")


class HubConfig(ContainerConfig):
    def __init__(self, image, capabilities, version="latest",
                 name="selenium-hub", host_port=4444, container_port=4444):
        super(HubConfig, self).__init__(image=image, version=version)
        self.host_port = host_port
        self.capabilities = capabilities
        self.name = name
        self.bind_ports(host_port, container_port)


class SeleniumGridContainers(GenericSeleniumContainer):
    HUB_IMAGE = "selenium/hub"
    FF_NODE_IMAGE = "selenium/node-firefox-debug"
    CHROME_NODE_IMAGE = "selenium/node-chrome-debug"

    def __init__(self, hub_config, node_config):
        super(SeleniumGridContainers, self).__init__(hub_config)
        self.hub = StandaloneSeleniumContainer(self.config)
        self.node = StandaloneSeleniumContainer(node_config)

    def start(self):
        self.hub.start()
        self.node.start()
        return self

    def stop(self):
        self.hub.stop()
        self.node.stop()

    def get_driver(self):
        return self.hub.get_driver()
