import logging
from time import sleep

from docker import Client
from selenium.webdriver import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class docker(object):
    def __init__(self, base_url='unix://var/run/docker.sock'):
        self.cli = Client(base_url)
        self.containers = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for cont in self.containers:
            self.cli.stop(cont)
            self.cli.remove_container(cont)

    def create_container(self, image, ports=None, port_bindings=None, name=None, links=None):
        host_config = self.cli.create_host_config(port_bindings=port_bindings)
        container = self.cli.create_container(image=image, ports=ports, host_config=host_config, name=name)

        self.cli.start(container, publish_all_ports=True, port_bindings=port_bindings, links=links)
        self.containers.append(container)
        return container

    def inspect(self, container):
        return self.cli.inspect_container(container)

    def get_host_info(self, container):
        return doc.inspect(container)

    def get_containers(self):
        return self.containers


# cli = Client(base_url='unix://var/run/docker.sock')
# container = cli.create_container('selenium/hub', ports=[4444])
# cli.start(container, publish_all_ports=True)
# info = cli.inspect_container(container)
# host_info = info['NetworkSettings']['Ports']['4444/tcp'][0]
# wd_hub = "http://{}:{}/wd/hub".format(host_info['HostIp'], host_info['HostPort'])
# print(wd_hub)
#
# sleep(5)
# driver = WebDriver(wd_hub, {"": ""})
#
# driver.get("http://google.com")
# driver.find_element_by_name("q").send_keys("Hello")
#
# cli.stop(container)


with docker() as doc:
    # hub = doc.create_container('selenium/hub')
    hub = doc.create_container('selenium/hub:latest', ports=[4444], port_bindings={4444: 4444}, name='selenium-hub')
    #node = doc.create_container('selenium/node-firefox:2.53.0', links={'selenium-hub': 'hub'})
    print(doc.get_containers())
    host_info = doc.get_host_info(hub)
    print(host_info)

    sleep(2)
    wd_hub = "http://{}:{}/wd/hub".format('localhost', 4444)

    driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4444/wd/hub',
        desired_capabilities=DesiredCapabilities.FIREFOX)
    logging.warn("Driver created")
    driver.get("http://google.com")
    logging.warn("URL opened")
    driver.find_element_by_name("qq").send_keys("Hello"+Keys.ENTER)
    logging.warn("finished")
    #sleep(60)
