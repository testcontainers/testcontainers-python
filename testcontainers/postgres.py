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
    def start(self):
        self._docker.run(**config.postgres_container)
        return self

    @wait_container_is_ready()
    def connection(self):
        return psycopg2.connect(self.image, **config.postgres_db)

    def __init__(self, version='latest', image="postgres"):
        super(PostgresDockerContainer, self).__init__()
        self.image = "{}:{}".format(image, version)
