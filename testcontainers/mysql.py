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
from os import environ

from testcontainers.core.generic import DbContainer


class MySqlContainer(DbContainer):

    MYSQL_ROOT_PASSWORD = environ.get("MYSQL_ROOT_PASSWORD", "test")
    MYSQL_DATABASE = environ.get("MYSQL_DATABASE", "test")
    MYSQL_USER = environ.get("MYSQL_USER", "test")
    MYSQL_PASSWORD = environ.get("MYSQL_PASSWORD", "test")

    def __init__(self, image="mysql:latest"):
        super(MySqlContainer, self).__init__(image,
                                             dialect="mysql+pymysql",
                                             username=self.MYSQL_ROOT_PASSWORD,
                                             password=self.MYSQL_PASSWORD,
                                             port=3306,
                                             db_name=self.MYSQL_DATABASE)

    def _configure(self):
        self.add_env("MYSQL_ROOT_PASSWORD", self.MYSQL_ROOT_PASSWORD)
        self.add_env("MYSQL_DATABASE", self.MYSQL_DATABASE)
        self.add_env("MYSQL_USER", self.MYSQL_USER)
        self.add_env("MYSQL_PASSWORD", self.MYSQL_PASSWORD)


class MariaDbContainer(MySqlContainer):
    def __init__(self, image="mariadb:latest"):
        super(MariaDbContainer, self).__init__(image)
