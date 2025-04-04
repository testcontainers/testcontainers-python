from testcontainers.core.config import MAX_TRIES
from testcontainers.core.generic import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class ScyllaContainer(DockerContainer):
    """
    Scylla database container.

    Example
    -------
    .. doctest::

        >>> from testcontainers.scylla import ScyllaContainer

        >>> with ScyllaContainer() as scylla:
        ...    cluster = scylla.get_cluster()
        ...    with cluster.connect() as session:
        ...        result = session.execute(
        ...            "CREATE KEYSPACE keyspace1 WITH replication "
        ...            "= {'class': 'SimpleStrategy', 'replication_factor': '1'};")
    """

    def __init__(self, image="scylladb/scylla:latest", ports_to_expose=(9042,)):
        super().__init__(image)
        self.ports_to_expose = ports_to_expose
        self.with_exposed_ports(*self.ports_to_expose)
        self.with_command("--skip-wait-for-gossip-to-settle=0")

    @wait_container_is_ready(OSError)
    def _connect(self):
        wait_for_logs(self, predicate="Starting listening for CQL clients", timeout=MAX_TRIES)
        cluster = self.get_cluster()
        cluster.connect()

    def start(self):
        super().start()
        self._connect()
        return self

    def get_cluster(self, **kwargs):
        from cassandra.cluster import Cluster

        hostname = self.get_container_host_ip()
        port = self.get_exposed_port(9042)
        return Cluster(contact_points=[hostname], port=port, **kwargs)
