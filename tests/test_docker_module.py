from time import sleep

from testcontainers_python.docker_client import DockerClient

# class App:
#     def __init__(self, smtp):
#         self.docker = smtp
#
# @pytest.fixture(scope="module")
# def app(smtp):
#     return App(smtp)
from testcontainers_python.webdriver_container import WebDriverContainer
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pytest


class TestDocker(object):
    @pytest.mark.parametrize("browser", [
        DesiredCapabilities.CHROME,
        DesiredCapabilities.FIREFOX,
    ])
    def test_selenium(self, browser):
        with WebDriverContainer(browser) as firefox:
            driver = firefox.get_driver()
            driver.get("http://google.com")
            driver.find_element_by_name("q").send_keys("Hello")
