import os

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from testcontainers import mysql

from testcontainers.core.generic import GenericContainer

from importlib import reload


def setup_module(m):
    os.environ["MYSQL_USER"] = "demo"
    os.environ["MYSQL_DATABASE"] = "custom_db"


def test_docker_custom_image():
    container = GenericContainer("spirogov/video_service:latest")
    container.with_bind_ports(8086, 8086)
    #container.with_name("video_service")
    container.with_volume_mapping("/Users/sepi/auto_env", "/root/video", mode='rw')

    with container:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.implicitly_wait(10)
        driver.get("http://localhost:8086")
        driver.find_element_by_css_selector("#inputEmail3").send_keys("admin")


def test_docker_env_variables():
    reload(mysql)

    db = mysql.MySqlContainer()
    db.with_bind_ports(3306, 32785)
    with db:
        url = db.get_connection_url()
        assert url == 'mysql+pymysql://demo:test@0.0.0.0:32785/custom_db'
