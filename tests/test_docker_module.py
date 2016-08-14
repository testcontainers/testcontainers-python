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


class TestDocker(object):

    def test_selenium(self):
        with WebDriverContainer() as firefox:
            driver = firefox.get_driver()
            driver.get("http://google.com")
            driver.find_element_by_name("q").send_keys("Hello")
