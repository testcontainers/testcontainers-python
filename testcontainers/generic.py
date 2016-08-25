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
        raise NotImplementedError

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
        raise NotImplementedError


class GenericDockerContainer(DockerContainer):
    def __init__(self, config):
        super(GenericDockerContainer, self).__init__()
        self.container = None
        self.config = config

    def start(self):
        """
        Start container without wait
        :return:
        """
        self.container = self._docker.run(**self.config)
        return self

    @property
    def id(self):
        return self.container["Id"]


class GenericDbContainer(DockerContainer):
    def __init__(self, config):
        super(GenericDbContainer, self).__init__(config)

    def start(self):
        """
        Start my sql container and wait to be ready
        :return:
        """
        self._docker.run(image=self.config.image,
                         env=self.config.env,
                         name=self.config.container_name,
                         bind_ports=self.config.port_bindings)
        self._connect()
        return self

    @wait_container_is_ready()
    def _connect(self):
        """
        dialect+driver://username:password@host:port/database
        :return:
        """
        engine = sqlalchemy.create_engine(
            "{}://{}:{}@{}/{}".format(self.config.container_name,
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

    @property
    def host_ip(self):
        return self._container_config.host_ip
