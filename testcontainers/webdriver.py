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

from testcontainers.core.generic import GenericSeleniumContainer


class SeleniumImage(object):
    STANDALONE_FIREFOX = "selenium/standalone-firefox-debug"
    STANDALONE_CHROME = "selenium/standalone-chrome-debug"
    HUB_IMAGE = "selenium/hub"
    FIREFOX_NODE = "selenium/node-firefox-debug"
    CHROME_NODE = "selenium/node-chrome-debug"

    def __init__(self):
        pass


class StandaloneSeleniumContainer(GenericSeleniumContainer):
    def __init__(self, image,
                 capabilities,
                 host_port=None,
                 container_port=4444,
                 host_vnc_port=None,
                 name=None,
                 version="latest"):
        super(StandaloneSeleniumContainer, self) \
            .__init__(image_name=image,
                      host_port=host_port,
                      container_port=container_port,
                      name=name,
                      version=version,
                      capabilities=capabilities,
                      host_vnc_port=host_vnc_port)


class SeleniumHub(GenericSeleniumContainer):
    def __init__(self, image,
                 capabilities,
                 host_port=None,
                 container_port=4444,
                 name="selenium-hub",
                 version="latest"):
        super(SeleniumHub, self).__init__(image_name=image,
                                          host_port=host_port,
                                          container_port=container_port,
                                          name=name,
                                          version=version,
                                          capabilities=capabilities,
                                          host_vnc_port=None)

        self._configure()

    def _configure(self):
        self.bind_ports(self.host_port, self.container_port)


class SeleniumNode(GenericSeleniumContainer):
    def __init__(self, image_name, version="latest"):
        super(SeleniumNode, self).__init__(image_name=image_name,
                                           capabilities=None,
                                           host_port=None,
                                           container_port=None,
                                           name=None,
                                           version=version,
                                           host_vnc_port=None)
        self.link_label = "hub"

    def link_to_hub(self, hub):
        self.link_containers(hub.container_name, self.link_label)


class SeleniumGrid(object):
    def __init__(self,
                 capabilities,
                 hub_image="selenium/hub",
                 host_port=4444,
                 container_port=4444,
                 name="selenium-hub",
                 version="latest", node_count=1):
        self.hub = SeleniumHub(hub_image,
                               capabilities=capabilities,
                               host_port=host_port,
                               container_port=container_port,
                               name=name,
                               version=version)
        self.node = SeleniumNode(self._get_node_image(), version=version)
        self.node_count = node_count

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        self.hub.start()
        self.node.link_to_hub(self.hub)
        for _ in range(self.node_count):
            self.node.start()
        return self

    def stop(self):
        self.hub.stop()
        self.node.stop()

    def _get_node_image(self):
        if self._is_chrome():
            return SeleniumImage.CHROME_NODE
        return SeleniumImage.FIREFOX_NODE

    def _is_chrome(self):
        return self.hub.capabilities["browserName"] == "chrome"

    def get_driver(self):
        return self.hub.get_driver()

    def get_info(self):
        return self.hub.inspect()

    def get_connection_url(self):
        return self.hub.get_connection_url()
