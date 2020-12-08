
def test_selenium_custom_image():
    from testcontainers.selenium import BrowserWebDriverContainer
    from selenium.webdriver import DesiredCapabilities

    image = "selenium/standalone-chrome:latest"
    chrome = BrowserWebDriverContainer(DesiredCapabilities.CHROME, image=image)
    assert "image" in dir(chrome), "`image` attribute was not instantialized."
    assert chrome.image == image, "`image` attribute was not set to the user provided value"
