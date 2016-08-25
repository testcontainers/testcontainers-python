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
