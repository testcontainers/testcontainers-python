from testcontainers.scylla import ScyllaContainer


def test_docker_run_scylla():
    with ScyllaContainer() as scylla:
        cluster = scylla.get_cluster()
        with cluster.connect() as session:
            session.execute(
                "CREATE KEYSPACE keyspace1 WITH replication = "
                "{'class': 'SimpleStrategy', 'replication_factor': '1'};"
            )
            session.execute("CREATE TABLE keyspace1.table1 (key1 int, key2 int, PRIMARY KEY (key1));")
            session.execute("INSERT INTO keyspace1.table1 (key1,key2) values (1,2);")

            response = session.execute("SELECT * FROM keyspace1.table1")

            assert response.one().key1 == 1
            assert response.one().key2 == 2
