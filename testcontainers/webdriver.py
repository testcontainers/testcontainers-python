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
from testcontainers.core.config import SeleniumConfig

from testcontainers.core.generic import GenericSeleniumContainer


class SeleniumImage(object):
    STANDALONE_FIREFOX = "selenium/standalone-firefox-debug"
    STANDALONE_CHROME = "selenium/standalone-chrome-debug"
    HUB_IMAGE = "selenium/hub"
    FIREFOX_NODE = "selenium/node-firefox-debug"
    CHROME_NODE = "selenium/node-chrome-debug"

    def __init__(self):
        pass


class StandaloneSeleniumConfig(SeleniumConfig):
    def __init__(self, image_name,
                 capabilities,
                 version="latest",
                 name=None,
                 host_port=4444,
                 container_port=4444,
                 host_vnc_port=5900,
                 container_vnc_port=5900):
        super(StandaloneSeleniumConfig, self). \
            __init__(image_name=image_name,
                     version=version,
                     name=name,
                     host_port=host_port,
                     container_port=container_port,
                     host_vnc_port=host_vnc_port,
                     container_vnc_port=container_vnc_port)

        self.capabilities = capabilities


class NodeConfig(SeleniumConfig):
    def __init__(self, image_name,
                 version="latest",
                 hub_name="selenium-hub",
                 host_vnc_port=None,
                 container_vnc_port=5900,
                 name=None):
        super(NodeConfig, self).__init__(image_name=image_name,
                                         version=version,
                                         name=name,
                                         host_vnc_port=host_vnc_port,
                                         container_vnc_port=container_vnc_port,
                                         host_port=None,
                                         container_port=None)
        self.link_containers(hub_name, "hub")


class HubConfig(SeleniumConfig):
    def __init__(self, image_name,
                 capabilities,
                 version="latest",
                 name="selenium-hub",
                 host_port=4444,
                 container_port=4444):
        super(HubConfig, self).__init__(image_name=image_name,
                                        version=version,
                                        host_port=host_port,
                                        container_port=container_port,
                                        name=name, host_vnc_port=None,
                                        container_vnc_port=None)
        self.capabilities = capabilities


class StandaloneSeleniumContainer(GenericSeleniumContainer):
    def __init__(self, config):
        super(StandaloneSeleniumContainer, self).__init__(config)


class SeleniumGridContainers(GenericSeleniumContainer):
    def __init__(self, hub_config, node_config, node_count=1):
        super(SeleniumGridContainers, self).__init__(hub_config)
        self.hub = StandaloneSeleniumContainer(self._config)
        self.node = StandaloneSeleniumContainer(node_config)
        self.node_count = node_count

    def start(self):
        self.hub.start()
        for _ in range(self.node_count):
            self.node.start()
        return self

    def stop(self):
        self.hub.stop()
        self.node.stop()

    def get_driver(self):
        return self.hub.get_driver()
