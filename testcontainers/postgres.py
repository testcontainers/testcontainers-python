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
import os

from testcontainers.core.generic import DbContainer


class PostgresContainer(DbContainer):
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "test")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "test")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "test")

    def __init__(self, image="postgres:latest"):
        super(PostgresContainer, self).__init__(image=image)
        self.port_to_expose = 5432

    def _configure(self):
        self.add_env("POSTGRES_USER", self.POSTGRES_USER)
        self.add_env("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self.add_env("POSTGRES_DB", self.POSTGRES_DB)

    def get_connection_url(self):
        super()._create_connection_url(dialect="postgresql+psycopg2",
                                       username=self.POSTGRES_USER,
                                       password=self.POSTGRES_PASSWORD,
                                       db_name=self.POSTGRES_DB,
                                       port=self.port_to_expose)
