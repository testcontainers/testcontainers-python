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
from testcontainers.core.generic import DbContainer


class MySqlContainer(DbContainer):
    def __init__(self, image="mysql", version="latest"):
        super(MySqlContainer, self).__init__(image,
                                             version,
                                             dialect="mysql+pymysql",
                                             username="test",
                                             password="test",
                                             port=3306,
                                             db_name="test")
        self.root_password = "test"
        self.host_port = 3306

    def _configure(self):
        self.expose_port("3306/tcp", self.port)
        self.add_env("MYSQL_ROOT_PASSWORD", self.root_password)
        self.add_env("MYSQL_DATABASE", self.db_name)
        self.add_env("MYSQL_USER", self.username)
        self.add_env("MYSQL_PASSWORD", self.password)


class MariaDbContainer(MySqlContainer):
    def __init__(self, image="mariadb", version="latest"):
        super(MariaDbContainer, self).__init__(image, version)
