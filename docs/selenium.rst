Selenium containers
===================

Allows to spin up Selenium Grid and Selenium standalone containers

Selenium Standalone example:
----------------------------
::

    import pytest
    from selenium.webdriver import DesiredCapabilities
    from testcontainers.selenium import BrowserWebDriverContainer


    def test_webdriver_container_container(caps):
        chrome = BrowserWebDriverContainer(esiredCapabilities.CHROME)

        with chrome:
            webdriver = chrome.get_driver()
            webdriver.get("http://google.com")
            webdriver.find_element_by_name("q").send_keys("Hello")

You can easily change browser by passing appropriate capabilities.

::

    import pytest
    from selenium.webdriver import DesiredCapabilities
    from testcontainers.selenium import BrowserWebDriverContainer


    def test_webdriver_container_container(caps):
        chrome = BrowserWebDriverContainer(esiredCapabilities.FIREFOX)

        with chrome:
            webdriver = chrome.get_driver()
            webdriver.get("http://google.com")
            webdriver.find_element_by_name("q").send_keys("Hello")

