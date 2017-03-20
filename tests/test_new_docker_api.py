from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from testcontainers.core.container import DockerContainer


def test_docker_custom_image():
    container = DockerContainer("spirogov/video_service", "latest").expose_port(8086, 8086)

    with container:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.implicitly_wait(10)
        driver.get("http://localhost:8086")
        driver.find_element_by_css_selector("#inputEmail3").send_keys("admin")