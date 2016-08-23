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
    def __init__(self):
        self._docker = DockerClient()
        self._image_name = None
        self._version = "latest"
        self._env = {}
        self._exposed_ports = {}
        self._host = "0.0.0.0"

    def __enter__(self):
        return self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

    def add_env(self, key, value):
        self._env[key] = value
        return self

    def bind_ports(self, host, container):
        self._exposed_ports[host] = container

    def start(self):
        raise NotImplementedError

    def stop(self):
        """
        Stop all spawned containers
        :return:
        """
        self._docker.remove_all_spawned()

    def _configure(self):
        raise NotImplementedError

    def _connect(self):
        raise NotImplementedError

    @property
    def _get_image(self):
        return "{}:{}".format(self._image_name, self._version)


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
    user = "test"
    passwd = "secret"

    def __init__(self):
        super(GenericDbContainer, self).__init__()

    def start(self):
        """
        Start my sql container and wait to be ready
        :return:
        """
        self._configure()
        self._docker.run(image=self._get_image,
                         env=self._env,
                         name=self._image_name,
                         bind_ports=self._exposed_ports)
        self._connect()
        return self

    @wait_container_is_ready()
    def _connect(self):
        """
        dialect+driver://username:password@host:port/database
        :return:
        """
        engine = sqlalchemy.create_engine(
            "{}://{}:{}@{}/{}".format(self._image_name,
                                      self.user,
                                      self.passwd,
                                      self._host,
                                      self.user))
        engine.connect()

    @property
    def username(self):
        return self.user

    @property
    def password(self):
        return self.passwd

    @property
    def db(self):
        return self.user

    @property
    def host(self):
        return self._host
