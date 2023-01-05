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

from neo4j import GraphDatabase

from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class Neo4jContainer(DbContainer):
    """
    Neo4j Graph Database (Standalone) database container.

    Example
    -------
    .. doctest::

        >>> from testcontainers.neo4j import Neo4jContainer

        >>> with Neo4jContainer() as neo4j, \
                    neo4j.get_driver() as driver, \
                    driver.session() as session:
        ...     result = session.run("MATCH (n) RETURN n LIMIT 1")
        ...     record = result.single()
    """

    # The official image requires a change of password on startup.
    NEO4J_ADMIN_PASSWORD = os.environ.get("NEO4J_ADMIN_PASSWORD", "password")

    # Default port for the binary Bolt protocol.
    DEFAULT_BOLT_PORT = 7687

    AUTH_FORMAT = "neo4j/{password}"

    NEO4J_STARTUP_TIMEOUT_SECONDS = 10

    NEO4J_USER = "neo4j"

    def __init__(self, image="neo4j:latest", **kwargs):
        super(Neo4jContainer, self).__init__(image, **kwargs)
        self.bolt_port = Neo4jContainer.DEFAULT_BOLT_PORT
        self.with_exposed_ports(self.bolt_port)
        self._driver = None

    def _configure(self):
        self.with_env(
            "NEO4J_AUTH",
            Neo4jContainer.AUTH_FORMAT.format(password=Neo4jContainer.NEO4J_ADMIN_PASSWORD)
        )

    def get_connection_url(self):
        return "{dialect}://{host}:{port}".format(
            dialect="bolt",
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.bolt_port),
        )

    @wait_container_is_ready()
    def _connect(self):
        # First we wait for Neo4j to say it's listening
        wait_for_logs(
            self,
            "Remote interface available at",
            Neo4jContainer.NEO4J_STARTUP_TIMEOUT_SECONDS,
        )

        # Then we actually check that the container really is listening
        with self.get_driver() as driver:
            # Drivers may or may not be lazy
            # force them to do a round trip to confirm neo4j is working
            with driver.session() as session:
                session.run("RETURN 1").single()

    def get_driver(self, **kwargs):
        return GraphDatabase.driver(
            self.get_connection_url(),
            auth=(Neo4jContainer.NEO4J_USER, Neo4jContainer.NEO4J_ADMIN_PASSWORD),
            **kwargs
        )
