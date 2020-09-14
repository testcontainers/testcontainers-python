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
from testcontainers.core.waiting_utils import wait_container_is_ready


class CassandraContainer(DbContainer):
    """
    Cassandra container.

    Example
    -------
    The example will spin up a Cassandra instance to which you can connect with the default username
    ('cassandra') and password ('cassandra').
    ::

        with CassandraContainer('cassandra:3.11.3') as cassandra:
            cluster = Cluster([cassandra.get_container_host_ip()], cassandra.get_port())
            with cluster.connect() as session:
                row = session.execute("SELECT release_version FROM system.local").one()
                assert row.release_version == '3.11.3'
            cluster.shutdown()
    """

    def __init__(self, image="cassandra:latest", **kwargs):
        super(CassandraContainer, self).__init__(image, **kwargs)
        self.port_to_expose = 9042
        self.with_exposed_ports(self.port_to_expose)

    def _configure(self):
        pass

    @wait_container_is_ready()
    def _connect(self):
        from cassandra.cluster import Cluster
        cluster = Cluster([self.get_container_host_ip()], self.get_port())
        with cluster.connect() as session:
            session.execute("SELECT * FROM system_schema.keyspaces")
        cluster.shutdown()

    def get_port(self):
        return self.get_exposed_port(self.port_to_expose)
