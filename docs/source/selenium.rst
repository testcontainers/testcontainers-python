Selenium containers
===================

Allows to spin up Selenium Grid and Selenium standalone containers

Selenium Standalone example:
----------------------------
::

    chrome = StandaloneSeleniumContainer(SeleniumImage.STANDALONE_CHROME,
                                         DesiredCapabilities.CHROME)
            with chrome as container:
            driver = container.get_driver()
            driver.get("http://google.com")
            driver.find_element_by_name("q").send_keys("Hello")

You can easily change browser by passing parameter SeleniumImage.STANDALONE_FIREFOX and appropriate capabilities.

Selenium Grid
-------------

::

     with SeleniumGrid(DesiredCapabilities.FIREFOX, node_count=3) as firefox:
            webdriver = firefox.get_driver()
            webdriver.get("http://google.com")
            webdriver.find_element_by_name("q").send_keys("Hello")

It will spin up Selenium Grid Hub and three Firefox nodes.