docker_base_url = 'unix://var/run/docker.sock'
max_tries = 120
sleep_time = 1


class ContainerConfig(object):
    def __init__(self, image_name, version):
        self._host_ip = "localhost"
        self._version = version
        self.host_port = None
        self.environment = {}
        self.port_bindings = {}
        self.volumes = {}
        self.container_name = None
        self.container_links = {}
        self.image_name = image_name

    def set_host_port(self, port):
        self.host_port = port

    def bind_ports(self, host, container):
        if host:
            self.port_bindings[host] = container

    def link_containers(self, target, current):
        self.container_links[target] = current

    def mount_volume(self, host, container):
        self.volumes[host] = container

    def add_env(self, key, value):
        if key not in self.environment.keys():
            self.environment[key] = value
        else:
            raise ValueError("Value {} has been initialized".format(key))

    def set_container_name(self, name):
        self.container_name = name

    @property
    def image(self):
        return "{}:{}".format(self.image_name, self._version)

    @property
    def host_ip(self):
        return self._host_ip


class DbConfig(ContainerConfig):
    def __init__(self, image_name, version):
        super(DbConfig, self).__init__(image_name=image_name, version=version)

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
    def __init__(self, image_name, name, host_port, container_port,
                 host_vnc_port, container_vnc_port, version="latest"):
        super(SeleniumConfig, self).__init__(image_name=image_name, version=version)
        self.set_container_name(name)
        self.set_host_port(host_port)
        self.bind_ports(host_port, container_port)
        self.bind_ports(host_vnc_port, container_vnc_port)
        # this is workaround due to bug in Selenium images
        self.add_env("no_proxy", "localhost")
        self.add_env("HUB_ENV_no_proxy", "localhost")
