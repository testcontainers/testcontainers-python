* Selenium containers

Allows to spin up Selenium Grid and Selenium standalone containers

Selenium Standalone example:
----------------------------

Using BrowserWebDriverContainer you can spin up standalone containers either with Chrome or Firefox browser.

Example with Chrome:

::

    import pytest
    from selenium.webdriver import DesiredCapabilities
    from testcontainers.selenium import BrowserWebDriverContainer


    def test_webdriver_container_container():
        chrome = BrowserWebDriverContainer(DesiredCapabilities.CHROME)

        with chrome:
            webdriver = chrome.get_driver()
            webdriver.get("http://google.com")
            webdriver.find_element_by_name("q").send_keys("Hello")

You can easily change browser by passing appropriate capabilities.

::

    import pytest
    from selenium.webdriver import DesiredCapabilities
    from testcontainers.selenium import BrowserWebDriverContainer


    def test_webdriver_container_container():
        chrome = BrowserWebDriverContainer(DesiredCapabilities.FIREFOX)

        with chrome:
            webdriver = chrome.get_driver()
            webdriver.get("http://google.com")
            webdriver.find_element_by_name("q").send_keys("Hello")

