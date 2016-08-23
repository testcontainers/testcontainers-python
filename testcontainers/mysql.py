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

import MySQLdb

from testcontainers.generic import DockerContainer
from testcontainers.waiting_utils import wait_container_is_ready


class MySqlDockerContainer(DockerContainer):
    image = "mysql"
    user = "test"
    passwd = "secret"

    def __init__(self, version="latest"):
        super(MySqlDockerContainer, self).__init__()
        self._version = version
        self._add_env("MYSQL_USER", self.user)
        self._add_env("MYSQL_PASSWORD", self.passwd)
        self._add_env("MYSQL_ROOT_PASSWORD", self.passwd)
        self._add_env("MYSQL_DATABASE", self.user)
        self._expose_port(3306)

    def start(self):
        """
        Start my sql container and wait to be ready
        :return:
        """
        self._docker.run(image="{}:{}".format(self.image, self._version),
                         env=self._env,
                         name=self.image,
                         bind_ports={self._exposed_port: self._exposed_port})
        self._connect()
        return self

    @wait_container_is_ready()
    def _connect(self):
        return MySQLdb.connect(host=self._host,
                               user=self.user,
                               passwd=self.passwd,
                               db=self.user)

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
