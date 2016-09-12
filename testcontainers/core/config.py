import logging

docker_base_url = 'unix://var/run/docker.sock'
max_tries = 120
sleep_time = 1


class ContainerConfig(object):
    def __init__(self, image_name, version, container_name):
        self._host_ip = "localhost"
        self._version = version
        self.environment = {}
        self.port_bindings = {}
        self.volumes = {}
        self.container_name = container_name
        self.container_links = {}
        self.image_name = image_name

    def bind_ports(self, host, container):
        if host:
            self.port_bindings[host] = container

    def link_containers(self, target, current):
        self.container_links[target] = current
        logging.warning("Container {} linked to {}".format(current, target))

    def mount_volume(self, host, container):
        self.volumes[host] = container

    def add_env(self, key, value):
        if key not in self.environment.keys():
            self.environment[key] = value
            logging.warning("Env variable {} set to {}".format(key, value))
        else:
            raise ValueError("Can't override {}. "
                             "It has been initialized".format(key))

    @property
    def image(self):
        return "{}:{}".format(self.image_name, self._version)

    @property
    def host_ip(self):
        return self._host_ip
