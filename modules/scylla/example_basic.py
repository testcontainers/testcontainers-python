import json
from datetime import datetime

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

from testcontainers.scylla import ScyllaContainer


def basic_example():
    with ScyllaContainer() as scylla:
        # Get connection parameters
        host = scylla.get_container_host_ip()
        port = scylla.get_exposed_port(scylla.port)
        username = scylla.username
        password = scylla.password

        # Create Scylla client
        auth_provider = PlainTextAuthProvider(username=username, password=password)
        cluster = Cluster([host], port=port, auth_provider=auth_provider)
        session = cluster.connect()
        print("Connected to Scylla")

        # Create keyspace
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS test_keyspace
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)
        print("Created keyspace")

        # Use keyspace
        session.set_keyspace("test_keyspace")

        # Create table
        session.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id UUID PRIMARY KEY,
                name text,
                value int,
                category text,
                created_at timestamp
            )
        """)
        print("Created table")

        # Insert test data
        test_data = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "test1",
                "value": 100,
                "category": "A",
                "created_at": datetime.utcnow(),
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "test2",
                "value": 200,
                "category": "B",
                "created_at": datetime.utcnow(),
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "name": "test3",
                "value": 300,
                "category": "A",
                "created_at": datetime.utcnow(),
            },
        ]

        insert_stmt = session.prepare("""
            INSERT INTO test_table (id, name, value, category, created_at)
            VALUES (uuid(), ?, ?, ?, ?)
        """)

        for data in test_data:
            session.execute(insert_stmt, (data["name"], data["value"], data["category"], data["created_at"]))
        print("Inserted test data")

        # Query data
        print("\nQuery results:")
        rows = session.execute("SELECT * FROM test_table WHERE category = 'A' ALLOW FILTERING")
        for row in rows:
            print(
                json.dumps(
                    {
                        "id": str(row.id),
                        "name": row.name,
                        "value": row.value,
                        "category": row.category,
                        "created_at": row.created_at.isoformat(),
                    },
                    indent=2,
                )
            )

        # Create materialized view
        session.execute("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS test_view AS
            SELECT category, name, value, created_at
            FROM test_table
            WHERE category IS NOT NULL AND name IS NOT NULL
            PRIMARY KEY (category, name)
        """)
        print("\nCreated materialized view")

        # Query materialized view
        print("\nMaterialized view results:")
        rows = session.execute("SELECT * FROM test_view WHERE category = 'A'")
        for row in rows:
            print(
                json.dumps(
                    {
                        "category": row.category,
                        "name": row.name,
                        "value": row.value,
                        "created_at": row.created_at.isoformat(),
                    },
                    indent=2,
                )
            )

        # Create secondary index
        session.execute("CREATE INDEX IF NOT EXISTS ON test_table (value)")
        print("\nCreated secondary index")

        # Query using secondary index
        print("\nQuery using secondary index:")
        rows = session.execute("SELECT * FROM test_table WHERE value > 150 ALLOW FILTERING")
        for row in rows:
            print(
                json.dumps(
                    {
                        "id": str(row.id),
                        "name": row.name,
                        "value": row.value,
                        "category": row.category,
                        "created_at": row.created_at.isoformat(),
                    },
                    indent=2,
                )
            )

        # Get table metadata
        table_meta = session.cluster.metadata.keyspaces["test_keyspace"].tables["test_table"]
        print("\nTable metadata:")
        print(f"Columns: {[col.name for col in table_meta.columns.values()]}")
        print(f"Partition key: {[col.name for col in table_meta.partition_key]}")
        print(f"Clustering key: {[col.name for col in table_meta.clustering_key]}")


if __name__ == "__main__":
    basic_example()
