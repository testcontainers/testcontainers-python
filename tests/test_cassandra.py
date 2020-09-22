from cassandra.cluster import Cluster

from testcontainers.cassandra import CassandraContainer


def test_docker_run_cassandra():
    with CassandraContainer('cassandra:3.11.8').with_max_heap_size(1) as cassandra:
        cluster = Cluster([cassandra.get_container_host_ip()], cassandra.get_port())
        with cluster.connect() as session:
            row = session.execute("SELECT release_version FROM system.local").one()
            assert row.release_version == '3.11.8'
        cluster.shutdown()
