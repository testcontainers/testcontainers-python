import pytest
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from testcontainers.selenium import BrowserWebDriverContainer
from testcontainers.core.utils import is_arm


@pytest.mark.parametrize("caps", [DesiredCapabilities.CHROME, DesiredCapabilities.FIREFOX])
def test_webdriver_container_container(caps):
    if is_arm():
        pytest.skip('https://github.com/SeleniumHQ/docker-selenium/issues/1076')

    with BrowserWebDriverContainer(caps).maybe_emulate_amd64() as chrome:
        webdriver = chrome.get_driver()
        webdriver.get("http://example.com")
        header = webdriver.find_element(By.TAG_NAME, "h1").text
        assert header == "Example Domain"


def test_selenium_custom_image():
    image = "selenium/standalone-chrome:latest"
    chrome = BrowserWebDriverContainer(DesiredCapabilities.CHROME, image=image)
    assert "image" in dir(chrome), "`image` attribute was not instantialized."
    assert chrome.image == image, "`image` attribute was not set to the user provided value"
