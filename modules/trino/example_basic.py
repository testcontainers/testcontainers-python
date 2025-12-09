import trino
from trino.exceptions import TrinoQueryError

from testcontainers.trino import TrinoContainer


def basic_example():
    with TrinoContainer() as trino_container:
        # Get connection parameters
        host = trino_container.get_container_host_ip()
        port = trino_container.get_exposed_port(trino_container.port)

        # Create Trino client
        conn = trino.dbapi.connect(host=host, port=port, user="test", catalog="memory", schema="default")
        cur = conn.cursor()

        # Create a test table
        try:
            cur.execute("""
                CREATE TABLE memory.default.test_table (
                    id BIGINT,
                    name VARCHAR,
                    value DOUBLE
                )
            """)
            print("Created test table")
        except TrinoQueryError as e:
            print(f"Table might already exist: {e}")

        # Insert test data
        test_data = [(1, "test1", 100.0), (2, "test2", 200.0), (3, "test3", 300.0)]

        for row in test_data:
            cur.execute("INSERT INTO memory.default.test_table VALUES (%s, %s, %s)", row)
        print("Inserted test data")

        # Query data
        cur.execute("SELECT * FROM memory.default.test_table ORDER BY id")
        rows = cur.fetchall()

        print("\nQuery results:")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Value: {row[2]}")

        # Execute a more complex query
        cur.execute("""
            SELECT
                name,
                AVG(value) as avg_value,
                COUNT(*) as count
            FROM memory.default.test_table
            GROUP BY name
            ORDER BY avg_value DESC
        """)

        print("\nAggregation results:")
        for row in cur.fetchall():
            print(f"Name: {row[0]}, Average Value: {row[1]}, Count: {row[2]}")

        # Clean up
        cur.close()
        conn.close()


if __name__ == "__main__":
    basic_example()
