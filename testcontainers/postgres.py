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


class PostgresContainer(DbContainer):
    def __init__(self, image="postgres", version="latest"):
        super(PostgresContainer, self).__init__(image=image,
                                                version=version,
                                                dialect="postgresql+psycopg2",
                                                username="test",
                                                password="test",
                                                db_name="test",
                                                port=5432)
        self.host_port = 5432

    def _configure(self):
        self.add_env("POSTGRES_USER", self.username)
        self.add_env("POSTGRES_PASSWORD", self.password)
        self.add_env("POSTGRES_DB", self.db_name)
        self.expose_port(self.port, self.host_port)
