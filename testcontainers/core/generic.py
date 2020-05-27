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

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
from deprecation import deprecated


class DbContainer(DockerContainer):
    def __init__(self, image):
        super(DbContainer, self).__init__(image)

    @wait_container_is_ready()
    def _connect(self):
        import sqlalchemy
        engine = sqlalchemy.create_engine(self.get_connection_url())
        engine.connect()

    def get_connection_url(self):
        raise NotImplementedError

    def _create_connection_url(self, dialect, username, password, port, db_name):
        host = self.get_container_host_ip()
        port = self.get_exposed_port(port)
        return "{dialect}://{username}:{password}@{host}:{port}/{db}".format(
            dialect=dialect, username=username, password=password, host=host, port=port, db=db_name
        )

    def start(self):
        self._configure()
        super().start()
        self._connect()
        return self

    def _configure(self):
        raise NotImplementedError


class GenericContainer(DockerContainer):
    @deprecated(details="use plain DockerContainer instead")
    def __init__(self, image):
        super(GenericContainer, self).__init__(image)
