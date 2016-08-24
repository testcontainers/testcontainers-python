from selenium.webdriver import DesiredCapabilities

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
    def env(self):
        return self._environment

    @property
    def container_name(self):
        return self._image_name

    @property
    def host_ip(self):
        return self._host


class MySqlConfig(ContainerConfig):
    mysql_user = "MYSQL_USER"
    mysql_password = "MYSQL_PASSWORD"
    mysql_root_password = "MYSQL_ROOT_PASSWORD"
    mysql_db_name = "MYSQL_DATABASE"
    _super_user_name = "root"

    def __init__(self, user, password, superuser=False, root_pass="secret", db="test", host_port=3306, image="mysql",
                 version="latest"):
        super(MySqlConfig, self).__init__(image, version)
        self.superuser = superuser
        if not superuser:
            self.add_env(self.mysql_user, user)
            self.add_env(self.mysql_password, password)
        self.add_env(self.mysql_root_password, root_pass)
        self.add_env(self.mysql_db_name, db)
        self.bind_ports(host_port, 3306)

    @property
    def username(self):
        if self.superuser:
            return self._super_user_name
        return self.env[self.mysql_user]

    @property
    def password(self):
        if self.superuser:
            return self.env[self.mysql_root_password]
        return self.env[self.mysql_password]

    @property
    def db(self):
        return self.env[self.mysql_db_name]


class SeleniumConfig(ContainerConfig):
    standalone_firefox = "selenium/standalone-firefox-debug"
    standalone_chrome = "selenium/standalone-chrome-debug"
    hub_port = 4444
    host_vnc_port = 5900
    container_vnc_port = 5900

    def __init__(self, image, capabilities, version="latest"):
        super(SeleniumConfig, self).__init__(image, version)
        self.capabilities = capabilities
