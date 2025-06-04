from datetime import datetime, timedelta

import pandas as pd
from clickhouse_driver import Client

from testcontainers.clickhouse import ClickHouseContainer


def basic_example():
    with ClickHouseContainer() as clickhouse:
        # Get connection parameters
        host = clickhouse.get_container_host_ip()
        port = clickhouse.get_exposed_port(clickhouse.port)

        # Create ClickHouse client
        client = Client(host=host, port=port)

        # Create a test table
        client.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id UInt32,
                name String,
                value Float64,
                timestamp DateTime
            ) ENGINE = MergeTree()
            ORDER BY (id, timestamp)
        """)
        print("Created test table")

        # Generate test data
        now = datetime.now()
        data = [
            (1, "test1", 100.0, now),
            (2, "test2", 200.0, now + timedelta(hours=1)),
            (3, "test3", 300.0, now + timedelta(hours=2)),
        ]

        # Insert data
        client.execute("INSERT INTO test_table (id, name, value, timestamp) VALUES", data)
        print("Inserted test data")

        # Query data
        result = client.execute("""
            SELECT *
            FROM test_table
            ORDER BY id
        """)

        print("\nQuery results:")
        for row in result:
            print(f"ID: {row[0]}, Name: {row[1]}, Value: {row[2]}, Timestamp: {row[3]}")

        # Execute a more complex query
        result = client.execute("""
            SELECT
                name,
                avg(value) as avg_value,
                min(value) as min_value,
                max(value) as max_value
            FROM test_table
            GROUP BY name
            ORDER BY avg_value DESC
        """)

        print("\nAggregation results:")
        for row in result:
            print(f"Name: {row[0]}, Avg: {row[1]:.2f}, Min: {row[2]:.2f}, Max: {row[3]:.2f}")

        # Convert to pandas DataFrame
        df = pd.DataFrame(result, columns=["name", "avg_value", "min_value", "max_value"])
        print("\nDataFrame:")
        print(df)


if __name__ == "__main__":
    basic_example()
