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

from testcontainers.docker_client import DockerClient
from testcontainers.waiting_utils import wait_container_is_ready


class DockerContainer(object):
    def __init__(self, config):
        self._docker = DockerClient()
        self._container_config = config

    def __enter__(self):
        return self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        self._docker.run(image=self.image,
                         bind_ports=self.port_bindings,
                         env=self.environment,
                         links=self.config.container_links,
                         name=self.container_name)
        return self

    def stop(self):
        """
        Stop all spawned containers
        :return:
        """
        self._docker.remove_all_spawned()

    @property
    def config(self):
        return self._container_config

    def _connect(self):
        raise NotImplementedError()

    @property
    def environment(self):
        return self.config.env

    @property
    def image(self):
        return self.config.image

    @property
    def image_name(self):
        return self.config.image_name

    @property
    def container_name(self):
        return self.config.container_name

    @property
    def port_bindings(self):
        return self.config.port_bindings

    @property
    def host_ip(self):
        return self.config.host_ip

    @property
    def host_port(self):
        return self.config.host_port


class GenericDbContainer(DockerContainer):
    def __init__(self, config):
        super(GenericDbContainer, self).__init__(config)

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
            "{}://{}:{}@{}/{}".format(self.image_name,
                                      self.username,
                                      self.password,
                                      self.host_ip,
                                      self.db))
        engine.connect()

    @property
    def db(self):
        return self.config.db

    @property
    def password(self):
        return self.config.password

    @property
    def username(self):
        return self.config.username


class GenericSeleniumContainer(DockerContainer):
    def __init__(self, config):
        super(GenericSeleniumContainer, self).__init__(config)

    @wait_container_is_ready()
    def _connect(self):
        return webdriver.Remote(
            command_executor=('http://{}:{}/wd/hub'.format(
                self.host_ip,
                self.host_port)
            ),
            desired_capabilities=self.config.capabilities)

    def get_driver(self):
        return self._connect()

    def _is_chrome(self):
        return self.config.capabilities["browserName"] == "chrome"
