from testcontainers.cassandra import CassandraContainer
import sys

from importlib.metadata import version
import pytest
from packaging.version import Version


@pytest.mark.skipif(
    Version(version("cassandra-driver")) <= Version("3.29.3") and sys.version_info > (3, 14),
    reason="cassandra-driver <= 3.29.3 is incompatible with Python > 3.14",
)
def test_docker_run_cassandra() -> None:
    from cassandra.cluster import Cluster, DCAwareRoundRobinPolicy

    with CassandraContainer("cassandra:4.1.4") as cassandra:
        cluster = Cluster(
            cassandra.get_contact_points(),
            load_balancing_policy=DCAwareRoundRobinPolicy(cassandra.get_local_datacenter()),
        )
        session = cluster.connect()
        result = session.execute("SELECT release_version FROM system.local;")
        assert result.one().release_version == "4.1.4"
