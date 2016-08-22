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

from testcontainers import config
from testcontainers.generic import DockerContainer
from testcontainers.waiting_utils import wait_container_is_ready


class MySqlDockerContainer(DockerContainer):
    def __init__(self, version='latest', image='mysql'):
        super(self.__class__, self).__init__()
        self.image = "{}:{}".format(image, version)

    def start(self):
        """
        Start my sql container and wait to be ready
        :return:
        """
        self._docker.run(self.image, **config.my_sql_container)
        return self

    @wait_container_is_ready()
    def connection(self):
        return MySQLdb.connect(**config.mysql_db)
