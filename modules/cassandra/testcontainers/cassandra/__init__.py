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
from testcontainers.core.waiting_utils import wait_for_logs


class CassandraContainer(DockerContainer):
    """
    Cassandra database container.

    Example:

        .. doctest::

            >>> from testcontainers.cassandra import CassandraContainer
            >>> from cassandra.cluster import Cluster, DCAwareRoundRobinPolicy

            >>> with CassandraContainer("cassandra:4.1.4") as cassandra, Cluster(
            ...    cassandra.get_contact_points(),
            ...    load_balancing_policy=DCAwareRoundRobinPolicy(cassandra.get_local_datacenter()),
            ... ) as cluster:
            ...    session = cluster.connect()
            ...    result = session.execute("SELECT release_version FROM system.local;")
            ...    result.one().release_version
            '4.1.4'
    """

    CQL_PORT = 9042
    DEFAULT_LOCAL_DATACENTER = "datacenter1"

    def __init__(self, image: str = "cassandra:latest", **kwargs) -> None:
        super().__init__(image=image, **kwargs)
        self.with_exposed_ports(self.CQL_PORT)
        self.with_env("JVM_OPTS", "-Dcassandra.skip_wait_for_gossip_to_settle=0 -Dcassandra.initial_token=0")
        self.with_env("HEAP_NEWSIZE", "128M")
        self.with_env("MAX_HEAP_SIZE", "1024M")
        self.with_env("CASSANDRA_ENDPOINT_SNITCH", "GossipingPropertyFileSnitch")
        self.with_env("CASSANDRA_DC", self.DEFAULT_LOCAL_DATACENTER)

    def _connect(self):
        wait_for_logs(self, "Startup complete")

    def start(self) -> "CassandraContainer":
        super().start()
        self._connect()
        return self

    def get_contact_points(self) -> list[tuple[str, int]]:
        return [(self.get_container_host_ip(), int(self.get_exposed_port(self.CQL_PORT)))]

    def get_local_datacenter(self) -> str:
        return self.env.get("CASSANDRA_DC", self.DEFAULT_LOCAL_DATACENTER)
