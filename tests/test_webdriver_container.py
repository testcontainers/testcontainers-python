from selenium.webdriver import DesiredCapabilities

from testcontainers.selenium import BrowserWebDriverContainer


def test_chrome_container():
    chrome = BrowserWebDriverContainer(DesiredCapabilities.CHROME)

    with chrome:
        webdriver = chrome.get_driver()
        webdriver.get("http://google.com")
        webdriver.find_element_by_name("q").send_keys("Hello")