from testcontainers.webdriver import WebDriverDockerContainer
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import pytest


@pytest.fixture
def selenium_container(request):
    container = WebDriverDockerContainer().start()

    def fin():
        container.stop()

    request.addfinalizer(fin)
    return container.driver


class TestDocker(object):
    @pytest.mark.parametrize("browser", [
        DesiredCapabilities.FIREFOX,
        DesiredCapabilities.CHROME,
    ])
    def test_selenium(self, browser):
        with WebDriverDockerContainer(browser) as firefox:
            webdriver = firefox.driver
            webdriver.get("http://google.com")
            webdriver.find_element_by_name("q").send_keys("Hello")

    def test_fixture(self, selenium_container):
        selenium_container.get("http://google.com")
        selenium_container.find_element_by_name("q").send_keys("Hello")

    def test_fixture_2(self, selenium_container):
        selenium_container.get("http://google.com")
        selenium_container.find_element_by_name("q").send_keys("Hello")
