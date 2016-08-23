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


import psycopg2

from testcontainers import config
from testcontainers.generic import DockerContainer
from testcontainers.waiting_utils import wait_container_is_ready


class PostgresDockerContainer(DockerContainer):
    user = "test"
    passwd = "secret"

    def __init__(self):
        super(PostgresDockerContainer, self).__init__()
        self._image = "postgres"

    def _configure(self):
        self.add_env("POSTGRES_USER", self.user)
        self.add_env("POSTGRES_PASSWORD", self.passwd)
        self.add_env("POSTGRES_DB", self.user)
        self.bind_ports({5432: 5432})

    def start(self):
        self._configure()
        self._docker.run(image="{}:{}".format(self._image, self._version),
                         env=self._env,
                         name=self._image,
                         bind_ports=self._exposed_ports)
        self._connect()
        return self

    @wait_container_is_ready()
    def _connect(self):
        return psycopg2.connect(host=self._host,
                                user=self.user,
                                password=self.passwd,
                                database=self.user)
