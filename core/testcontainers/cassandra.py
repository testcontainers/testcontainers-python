from testcontainers.core.config import MAX_TRIES
from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class CassandraContainer(DockerContainer):
    """
    Cassandra database container.

    Example
    -------
    .. doctest::

        >>> from testcontainers.cassandra import CassandraContainer

        >>> with CassandraContainer() as cassandra:
        ...     cluster = cassandra.get_cluster()
        ...     with cluster.connect() as session:
        ...          result = session.execute(
        ...             "CREATE KEYSPACE keyspace1 WITH replication = "
        ...             "{'class': 'SimpleStrategy', 'replication_factor': '1'};")
    """
    def __init__(self, image="rinscy/cassandra:latest", ports_to_expose=[9042]):
        super(CassandraContainer, self).__init__(image)
        self.ports_to_expose = ports_to_expose
        self.with_exposed_ports(*self.ports_to_expose)

    @wait_container_is_ready()
    def _connect(self):
        wait_for_logs(
            self,
            predicate="Starting listening for CQL clients",
            timeout=MAX_TRIES)
        cluster = self.get_cluster()
        cluster.connect()

    def start(self):
        super(CassandraContainer, self).start()
        self._connect()
        return self

    def get_cluster(self, **kwargs):
        from cassandra.cluster import Cluster
        container = self.get_wrapped_container()
        container.reload()
        hostname = container.attrs['NetworkSettings']['IPAddress']
        return Cluster(contact_points=[hostname], **kwargs)
