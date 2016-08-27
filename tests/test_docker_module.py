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


import pytest
from selenium.webdriver import DesiredCapabilities

from testcontainers.webdriver import SeleniumImage, SeleniumHub, SeleniumNode, SeleniumGrid
from testcontainers.webdriver import StandaloneSeleniumContainer


@pytest.fixture
def selenium_container(request):
    pass
    # hub_config = HubConfig(SeleniumImage.HUB_IMAGE, DesiredCapabilities.FIREFOX)
    # node_config = NodeConfig(SeleniumImage.FIREFOX_NODE)
    # container = SeleniumGrid(hub_config, node_config).start()

    # def fin():
    #    container.stop()

    # request.addfinalizer(fin)
    # return container


class TestDocker(object):
    def test_selenium_grid(self):
        hub = SeleniumHub(SeleniumImage.HUB_IMAGE, DesiredCapabilities.FIREFOX)
        node = SeleniumNode(SeleniumImage.FIREFOX_NODE)
        with SeleniumGrid(hub, node, node_count=3) as firefox:
            webdriver = firefox.get_driver()
            webdriver.get("http://google.com")
            webdriver.find_element_by_name("q").send_keys("Hello")

    def test_fixture(self, selenium_container):
        driver = selenium_container.get_driver()
        driver.get("http://google.com")
        driver.find_element_by_name("q").send_keys("Hello")

    def test_standalone_container(self):
        chrome = StandaloneSeleniumContainer(SeleniumImage.STANDALONE_CHROME, DesiredCapabilities.CHROME)
        with chrome as container:
            driver = container.get_driver()
            driver.get("http://google.com")
            driver.find_element_by_name("q").send_keys("Hello")
