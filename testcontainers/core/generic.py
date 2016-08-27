#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import sqlalchemy
from selenium import webdriver

from testcontainers.core.config import ContainerConfig
from testcontainers.core.docker_client import DockerClient

from testcontainers.core.waiting_utils import wait_container_is_ready


class DockerContainer(object):
    def __init__(self, image_name, version, container_name, host_port):
        self._docker = DockerClient()
        self._config = ContainerConfig(image_name=image_name,
                                       version=version,
                                       container_name=container_name,
                                       host_port=host_port)

    def __enter__(self):
        return self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        self._docker.run(image=self._config.image,
                         bind_ports=self._config.port_bindings,
                         env=self._config.environment,
                         links=self._config.container_links,
                         name=self._config.container_name)
        return self

    def stop(self):
        self._docker.remove_all_spawned()

    @property
    def host_ip(self):
        return self._config.host_ip

    @property
    def host_port(self):
        return self._config.host_port

    def get_env(self, key):
        return self._config.environment[key]

    def add_env(self, key, value):
        self._config.add_env(key, value)

    def bind_ports(self, host, container):
        self._config.bind_ports(host, container)

    def mount_volume(self, host, container):
        self._config.mount_volume(host, container)

    def link_to_container(self, name):
        self._config.link_containers(name, self._config.container_name)


class GenericDbContainer(DockerContainer):
    def __init__(self, image_name,
                 version,
                 host_port,
                 user,
                 password,
                 database,
                 root_password, name):
        super(GenericDbContainer, self).__init__(image_name=image_name,
                                                 version=version,
                                                 host_port=host_port,
                                                 container_name=name)
        self.username = user
        self.password = password
        self.database = database
        self.root_password = root_password

    def start(self):
        """
        Start my sql container and wait to be ready
        :return:
        """
        super(GenericDbContainer, self).start()
        self._connect()
        return self

    @wait_container_is_ready()
    def _connect(self):
        """
        dialect+driver://username:password@host:port/database
        :return:
        """
        engine = sqlalchemy.create_engine(
            "{}://{}:{}@{}/{}".format(self._config.image_name,
                                      self.username,
                                      self.password,
                                      self.host_ip,
                                      self.database))
        engine.connect()

    def _configure(self):
        raise NotImplementedError()

    @property
    def host_ip(self):
        return "0.0.0.0"


class GenericSeleniumContainer(DockerContainer):
    def __init__(self, image_name,
                 capabilities,
                 version="latest",
                 name=None,
                 host_port=4444,
                 container_port=4444,
                 host_vnc_port=5900,
                 container_vnc_port=5900):
        super(GenericSeleniumContainer, self).__init__(image_name=image_name,
                                                       version=version,
                                                       host_port=host_port,
                                                       container_name=name)
        self.capabilities = capabilities
        self.container_port = container_port
        self.host_vnc_port = host_vnc_port
        self.container_vnc_port = container_vnc_port

    @wait_container_is_ready()
    def _connect(self):
        return webdriver.Remote(
            command_executor=('http://{}:{}/wd/hub'.format(
                self.host_ip,
                self.host_port)
            ),
            desired_capabilities=self.capabilities)

    def get_driver(self):
        return self._connect()

    def _is_chrome(self):
        return self.capabilities["browserName"] == "chrome"
