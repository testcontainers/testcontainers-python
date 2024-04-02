import pytest

from cassandra.cluster import Cluster, DCAwareRoundRobinPolicy

from testcontainers.cassandra import CassandraContainer


@pytest.mark.parametrize("version", ["4.1.4", "3.11.16"])
def test_docker_run_cassandra(version: str):
    with CassandraContainer(f"cassandra:{version}") as cassandra:
        cluster = Cluster(
            cassandra.get_contact_points(),
            load_balancing_policy=DCAwareRoundRobinPolicy(cassandra.get_local_datacenter()),
        )
        session = cluster.connect()
        result = session.execute("SELECT release_version FROM system.local;")
        assert result.one().release_version == version
