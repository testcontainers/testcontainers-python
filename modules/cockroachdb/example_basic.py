import pandas as pd
import sqlalchemy
from sqlalchemy import text

from testcontainers.cockroachdb import CockroachContainer


def basic_example():
    with CockroachContainer() as cockroach:
        # Get connection URL
        connection_url = cockroach.get_connection_url()

        # Create SQLAlchemy engine
        engine = sqlalchemy.create_engine(connection_url)

        # Create a test table
        with engine.begin() as conn:
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50),
                    value DECIMAL(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            )
            print("Created test table")

            # Insert test data
            test_data = [(1, "test1", 100.0), (2, "test2", 200.0), (3, "test3", 300.0)]

            conn.execute(
                text("""
                    INSERT INTO test_table (id, name, value)
                    VALUES (:id, :name, :value)
                """),
                [{"id": item_id, "name": name, "value": value} for item_id, name, value in test_data],
            )
            print("Inserted test data")

        # Query data
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                SELECT *
                FROM test_table
                ORDER BY id
            """)
            )

            print("\nQuery results:")
            for row in result:
                print(f"ID: {row.id}, Name: {row.name}, Value: {row.value}, Created: {row.created_at}")

        # Execute a more complex query
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                SELECT
                    name,
                    AVG(value) as avg_value,
                    COUNT(*) as count,
                    MIN(created_at) as first_created,
                    MAX(created_at) as last_created
                FROM test_table
                GROUP BY name
                ORDER BY avg_value DESC
            """)
            )

            print("\nAggregation results:")
            for row in result:
                print(
                    f"Name: {row.name}, "
                    f"Avg: {row.avg_value:.2f}, "
                    f"Count: {row.count}, "
                    f"First: {row.first_created}, "
                    f"Last: {row.last_created}"
                )

        # Convert to pandas DataFrame
        with engine.connect() as conn:
            df = pd.read_sql("SELECT * FROM test_table ORDER BY id", conn)
            print("\nDataFrame:")
            print(df)


if __name__ == "__main__":
    basic_example()
