from selenium.webdriver import DesiredCapabilities

from testcontainers.exceptions import NoSuchBrowserException

docker_base_url = 'unix://var/run/docker.sock'
max_tries = 120
sleep_time = 1


class ContainerConfig(object):
    def __init__(self, image, version):
        self._host = "0.0.0.0"
        self._version = version
        self._image_name = image
        self._environment = {}
        self._port_bindings = {}
        self._volumes = {}
        self._links = {}

    def bind_ports(self, host, container):
        self._port_bindings[host] = container

    def link_containers(self, target, current):
        self._links[target] = current

    def mount_volume(self, host, container):
        self._volumes[host] = container

    def add_env(self, key, value):
        self._environment[key] = value
        return self

    @property
    def port_bindings(self):
        return self._port_bindings

    @property
    def image(self):
        return "{}:{}".format(self._image_name, self._version)

    @property
    def version(self):
        return self._version

    @property
    def env(self):
        return self._environment

    @property
    def container_name(self):
        return self._image_name

    @property
    def container_links(self):
        return self._links

    @property
    def host_ip(self):
        return self._host





class SeleniumConfig(ContainerConfig):
    HUB_IMAGE = "selenium/hub"
    FF_NODE_IMAGE = "selenium/node-firefox-debug"
    CHROME_NODE_IMAGE = "selenium/node-chrome-debug"
    FIREFOX = "selenium/standalone-firefox-debug"
    CHROME = "selenium/standalone-chrome-debug"

    def __init__(self, image, capabilities=None, hub_host_port=4444,
                 hub_container_port=4444, hub_container_name="selenium-hub",
                 vnc_host_port=5900, vnc_container_port=5900,
                 version="latest"):
        super(SeleniumConfig, self).__init__(image, version)
        self.capabilities = capabilities if \
            capabilities else self._get_capabilities_for(image)
        self.hub_container_port = hub_container_port
        self.vnc_container_port = vnc_container_port
        self.hub_host_port = hub_host_port
        self.hub_container_name = hub_container_name
        self.vnc_host_port = vnc_host_port
        self.bind_ports(hub_host_port, self.hub_container_port)
        self.bind_ports(vnc_host_port, self.vnc_container_port)
        self.add_env("no_proxy", "localhost")
        self.add_env("HUB_ENV_no_proxy", "localhost")

    def _get_capabilities_for(self, image):
        if str(image).__contains__("chrome"):
            return DesiredCapabilities.FIREFOX
        elif str(image).__contains__("firefox"):
            return DesiredCapabilities.FIREFOX
        else:
            raise NoSuchBrowserException("No capabilities for "
                                         "image {}".format(image))
