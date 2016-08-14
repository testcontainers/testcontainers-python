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
    _ff = WebDriverContainer().start()

    def test_selenium(self):
        try:
            driver = self._ff.get_driver()
            driver.get("http://google.com")
            driver.find_element_by_name("q").send_keys("Hello")
        finally:
            self._ff._docker.remove_all()
