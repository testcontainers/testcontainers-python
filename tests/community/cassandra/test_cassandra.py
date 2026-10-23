from testcontainers.community.cassandra import CassandraContainer


def test_docker_run_cassandra() -> None:
    from cassandra.cluster import Cluster, DCAwareRoundRobinPolicy

    with (
        CassandraContainer("cassandra:4.1.4") as cassandra,
        Cluster(
            cassandra.get_contact_points(),
            load_balancing_policy=DCAwareRoundRobinPolicy(cassandra.get_local_datacenter()),
            protocol_version=5,
        ) as cluster,
    ):
        session = cluster.connect()
        result = session.execute("SELECT release_version FROM system.local;")
        assert result.one().release_version == "4.1.4"
