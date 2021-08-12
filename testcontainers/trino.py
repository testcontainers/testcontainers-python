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
import re
import time

from sqlalchemy import create_engine

from testcontainers.core.exceptions import TimeoutException
from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class TrinoContainer(DbContainer):
    TRINO_STARTUP_TIMEOUT_SECONDS = 120

    def __init__(self, image="trinodb/trino:latest"):
        super(TrinoContainer, self).__init__(image=image)
        self.port_to_expose = 8080
        self.with_exposed_ports(self.port_to_expose)

    @wait_container_is_ready()
    def _connect(self):
        deadline = time.time() + TrinoContainer.TRINO_STARTUP_TIMEOUT_SECONDS
        regex = re.compile(".*======== SERVER STARTED ========.*", re.MULTILINE).search

        wait_for_logs(self, regex, TrinoContainer.TRINO_STARTUP_TIMEOUT_SECONDS)

        while time.time() < deadline:
            engine = create_engine(self.get_connection_url())
            engine.execute("SELECT 1")
            return

        raise TimeoutException(
            "Trino did not start within %.3f seconds" % TrinoContainer.TRINO_STARTUP_TIMEOUT_SECONDS
        )

    def get_connection_url(self):
        return "{dialect}://{host}:{port}".format(
            dialect="trino",
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.port_to_expose),
        )

    def _configure(self):
        pass
