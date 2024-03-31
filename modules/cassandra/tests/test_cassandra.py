from cassandra.cluster import Cluster, DCAwareRoundRobinPolicy

from testcontainers.cassandra import CassandraContainer


def test_docker_run_cassandra():
    with CassandraContainer("cassandra:4.1.4") as cassandra:
        cluster = Cluster(
            cassandra.get_contact_points(),
            load_balancing_policy=DCAwareRoundRobinPolicy(cassandra.get_local_datacenter()),
        )
        session = cluster.connect()
        result = session.execute("SELECT release_version FROM system.local;")
        assert result.one().release_version == "4.1.4"
