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
        self._container_name = None
        self._links = {}

    def bind_ports(self, host, container):
        if host:
            self._port_bindings[host] = container

    def link_containers(self, target, current):
        self._links[target] = current

    def mount_volume(self, host, container):
        self._volumes[host] = container

    def add_env(self, key, value):
        self._environment[key] = value
        return self

    def set_container_name(self, name):
        self._container_name = name

    @property
    def port_bindings(self):
        return self._port_bindings

    @property
    def image(self):
        return "{}:{}".format(self._image_name, self._version)

    @property
    def image_name(self):
        return self._image_name

    @property
    def version(self):
        return self._version

    @property
    def env(self):
        return self._environment

    @property
    def container_name(self):
        return self._container_name

    @property
    def container_links(self):
        return self._links

    @property
    def host_ip(self):
        return self._host


class DbConfig(ContainerConfig):
    def __init__(self, image, version):
        super(DbConfig, self).__init__(image=image, version=version)

    @property
    def username(self):
        raise NotImplementedError()

    @property
    def password(self):
        raise NotImplementedError()

    @property
    def db(self):
        raise NotImplementedError()


class SeleniumConfig(ContainerConfig):
    def __init__(self, image, name, host_port, container_port,
                 host_vnc_port, container_vnc_port, version="latest"):
        super(SeleniumConfig, self).__init__(image=image, version=version)
        self.set_container_name(name)
        self.host_port = host_port
        self.bind_ports(host_port, container_port)
        self.bind_ports(host_vnc_port, container_vnc_port)
        self.add_env("no_proxy", "localhost")  # this is workaround due to bug in Selenium images
        self.add_env("HUB_ENV_no_proxy", "localhost")
