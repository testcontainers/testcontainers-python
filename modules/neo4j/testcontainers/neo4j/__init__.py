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
from typing import Optional

from neo4j import Driver, GraphDatabase
from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class Neo4jContainer(DbContainer):
    """
    Neo4j Graph Database (Standalone) database container.

    Example:

        .. doctest::

            >>> from testcontainers.neo4j import Neo4jContainer

            >>> with Neo4jContainer() as neo4j, \\
            ...         neo4j.get_driver() as driver, \\
            ...         driver.session() as session:
            ...     result = session.run("MATCH (n) RETURN n LIMIT 1")
            ...     record = result.single()
    """

    def __init__(
        self,
        image: str = "neo4j:latest",
        port: int = 7687,
        password: Optional[str] = None,
        username: Optional[str] = None,
        **kwargs,
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "bolt_port", "port")
        super().__init__(image, **kwargs)
        self.username = username or os.environ.get("NEO4J_USER", "neo4j")
        self.password = password or os.environ.get("NEO4J_PASSWORD", "password")
        self.port = port
        self.with_exposed_ports(self.port)
        self._driver = None

    def _configure(self) -> None:
        self.with_env("NEO4J_AUTH", f"neo4j/{self.password}")

    def get_connection_url(self) -> str:
        return f"bolt://{self.get_container_host_ip()}:{self.get_exposed_port(self.port)}"

    @wait_container_is_ready()
    def _connect(self) -> None:
        wait_for_logs(self, "Remote interface available at", c.timeout)

        # Then we actually check that the container really is listening
        with self.get_driver() as driver:
            # Drivers may or may not be lazy
            # force them to do a round trip to confirm neo4j is working
            driver.verify_connectivity()

    def get_driver(self, **kwargs) -> Driver:
        return GraphDatabase.driver(self.get_connection_url(), auth=(self.username, self.password), **kwargs)
