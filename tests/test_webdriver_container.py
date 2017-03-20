import pytest
from selenium.webdriver import DesiredCapabilities
from testcontainers.selenium import BrowserWebDriverContainer


@pytest.mark.parametrize("caps", [DesiredCapabilities.CHROME, DesiredCapabilities.FIREFOX])
def test_webdriver_container_container(caps):
    chrome = BrowserWebDriverContainer(caps)

    with chrome:
        webdriver = chrome.get_driver()
        webdriver.get("http://google.com")
        webdriver.find_element_by_name("q").send_keys("Hello")
