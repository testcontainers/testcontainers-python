import pytest
from selenium.webdriver import DesiredCapabilities
from testcontainers.selenium import BrowserWebDriverContainer
from testcontainers.core.utils import is_arm


@pytest.mark.parametrize("caps", [DesiredCapabilities.CHROME, DesiredCapabilities.FIREFOX])
def test_webdriver_container_container(caps):
    if is_arm():
        pytest.skip('https://github.com/SeleniumHQ/docker-selenium/issues/1076')

    with BrowserWebDriverContainer(caps).maybe_emulate_amd64() as chrome:
        webdriver = chrome.get_driver()
        webdriver.get("http://google.com")
        webdriver.find_element_by_name("q").send_keys("Hello")
