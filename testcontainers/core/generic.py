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
import logging

import sqlalchemy
from selenium import webdriver

from testcontainers.core.config import ContainerConfig
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.waiting_utils import wait_container_is_ready


class DockerContainer(object):
    def __init__(self, image_name, version, container_name):
        self._docker = DockerClient()
        self._config = ContainerConfig(image_name=image_name,
                                       version=version,
                                       container_name=container_name)
        self._container = None

    def __enter__(self):
        return self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        self._container = self._docker.run(image=self._config.image,
                                           bind_ports=self._config.port_bindings,
                                           env=self._config.environment,
                                           links=self._config.container_links,
                                           name=self._config.container_name,
                                           volumes=self._config.volumes)
        self.print_ports()
        return self

    def print_ports(self):
        logging.warning("Container port mappings {}".format(
            self.inspect()['NetworkSettings']['Ports']))

    def stop(self):
        self._docker.stop(self._container)

    def get_host_info(self, port):
        info = self._docker.port(self._container, port)
        return info[0]

    def get_host_port(self, port):
        return self.get_host_info(port)['HostPort']

    def get_host_ip(self, port):
        return self.get_host_info(port)['HostIp']

    @property
    def container_name(self):
        return self._config.container_name

    def get_env(self, key):
        return self._config.environment[key]

    def add_env(self, key, value):
        self._config.add_env(key, value)

    def bind_ports(self, host, container):
        self._config.bind_ports(host, container)

    def mount_volume(self, host, container):
        self._config.mount_volume(host, container)

    def link_containers(self, target, current):
        self._config.link_containers(target, current)

    def inspect(self):
        return self._docker.inspect(self._container)


class GenericDbContainer(DockerContainer):
    def __init__(self, image_name,
                 version,
                 host_port,
                 name,
                 db_dialect,
                 username=None,
                 password=None,
                 database=None,
                 root_password=None):
        super(GenericDbContainer, self).__init__(image_name=image_name,
                                                 version=version,
                                                 container_name=name)
        self.host_port = host_port
        self.username = username
        self.password = password
        self.database = database
        self.root_password = root_password
        self.db_dialect = db_dialect

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
        engine = sqlalchemy.create_engine(self.get_connection_url())
        engine.connect()

    def _configure(self):
        raise NotImplementedError()

    @property
    def host_ip(self):
        return "0.0.0.0"

    def get_connection_url(self):
        return "{lang}://{username}" \
               ":{password}@{host}:" \
               "{port}/{db}".format(lang=self.db_dialect,
                                    username=self.username,
                                    password=self.password,
                                    host=self.host_ip,
                                    port=self.host_port,
                                    db=self.database)


class GenericSeleniumContainer(DockerContainer):
    def __init__(self, image_name,
                 capabilities,
                 host_port,
                 container_port,
                 name,
                 host_vnc_port,
                 version="latest",
                 container_vnc_port=5900):
        super(GenericSeleniumContainer, self).__init__(image_name=image_name,
                                                       version=version,
                                                       container_name=name)
        self.host_port = host_port
        self.capabilities = capabilities
        self.container_port = container_port
        self.host_vnc_port = host_vnc_port
        self.container_vnc_port = container_vnc_port
        self._add_env()
        self.bind_ports(host_port, container_port)
        self.bind_ports(host_vnc_port, container_vnc_port)

    def _add_env(self):
        # this is workaround due to bug in Selenium images
        self.add_env("no_proxy", "localhost")
        self.add_env("HUB_ENV_no_proxy", "localhost")

    @wait_container_is_ready()
    def _connect(self):
        return webdriver.Remote(
            command_executor=(self.get_connection_url()),
            desired_capabilities=self.capabilities)

    def get_driver(self):
        return self._connect()

    def get_connection_url(self):
        ip = self.get_host_ip(self.container_port)
        port = self.get_host_port(self.container_port)
        return 'http://{}:{}/wd/hub'.format(ip, port)

    def _is_chrome(self):
        return self.capabilities["browserName"] == "chrome"
