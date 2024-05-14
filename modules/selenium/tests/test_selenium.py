import os
import tempfile
from pathlib import Path

import pytest
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By

from testcontainers.core.utils import is_arm
from testcontainers.selenium import BrowserWebDriverContainer


@pytest.mark.parametrize("caps", [DesiredCapabilities.CHROME, DesiredCapabilities.FIREFOX])
def test_webdriver_container_container(caps):
    if is_arm():
        pytest.skip("https://github.com/SeleniumHQ/docker-selenium/issues/1076")

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


@pytest.mark.parametrize("caps", [DesiredCapabilities.CHROME, DesiredCapabilities.FIREFOX])
def test_selenium_video(caps, workdir):
    video_path = workdir / Path("video.mp4")
    with BrowserWebDriverContainer(caps).with_video(video_path=video_path) as chrome:
        chrome.get_driver().get("https://google.com")

    assert video_path.exists(), "Selenium video file does not exist"


@pytest.fixture
def workdir() -> Path:
    tmpdir = tempfile.TemporaryDirectory()
    # Enable write permissions for the Docker user container.
    os.chmod(tmpdir.name, 0o777)
    yield Path(tmpdir.name)
    tmpdir.cleanup()
