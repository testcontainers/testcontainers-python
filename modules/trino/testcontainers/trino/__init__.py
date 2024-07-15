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

from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs
from trino.dbapi import connect


class TrinoContainer(DbContainer):
    def __init__(
        self,
        image="trinodb/trino:latest",
        user: str = "test",
        port: int = 8080,
        **kwargs,
    ):
        super().__init__(image=image, **kwargs)
        self.user = user
        self.port = port
        self.with_exposed_ports(self.port)

    @wait_container_is_ready()
    def _connect(self) -> None:
        wait_for_logs(
            self,
            re.compile(".*======== SERVER STARTED ========.*", re.MULTILINE).search,
            c.max_tries,
            c.sleep_time,
        )
        conn = connect(
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.port),
            user=self.user,
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchall()
        conn.close()

    def get_connection_url(self):
        return f"trino://{self.user}@{self.get_container_host_ip()}:{self.port}"

    def _configure(self):
        pass
