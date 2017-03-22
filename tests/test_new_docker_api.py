from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from testcontainers.core.generic import GenericContainer
from testcontainers.mysql import MySqlContainer


def test_docker_custom_image():
    container = GenericContainer("spirogov/video_service:latest").bind_ports(8086, 8086)

    with container:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.implicitly_wait(10)
        driver.get("http://localhost:8086")
        driver.find_element_by_css_selector("#inputEmail3").send_keys("admin")


def test_docker_env_variables():
    mysql = MySqlContainer()
    mysql.MYSQL_DATABASE = "custom_db"
    mysql.bind_ports(3306, 32785)

    with mysql:
        url = mysql.get_connection_url()
        assert url == 'mysql+pymysql://test:test@0.0.0.0:32785/custom_db'
