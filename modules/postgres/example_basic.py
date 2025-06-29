import pandas as pd
import sqlalchemy
from sqlalchemy import text

from testcontainers.postgres import PostgresContainer


def basic_example():
    with PostgresContainer() as postgres:
        # Get connection URL
        connection_url = postgres.get_connection_url()

        # Create SQLAlchemy engine
        engine = sqlalchemy.create_engine(connection_url)
        print("Connected to PostgreSQL")

        # Create a test table
        create_table_sql = """
        CREATE TABLE test_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            value DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        with engine.begin() as connection:
            connection.execute(text(create_table_sql))
            print("Created test table")

        # Insert test data
        test_data = [
            {"name": "test1", "value": 100.0},
            {"name": "test2", "value": 200.0},
            {"name": "test3", "value": 300.0},
        ]

        with engine.begin() as connection:
            for data in test_data:
                connection.execute(text("INSERT INTO test_table (name, value) VALUES (:name, :value)"), data)
            print("Inserted test data")

        # Query data
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM test_table ORDER BY id"))
            rows = result.fetchall()

            print("\nQuery results:")
            for row in rows:
                print(f"ID: {row[0]}, Name: {row[1]}, Value: {row[2]}, Created: {row[3]}")

        # Execute a more complex query
        with engine.connect() as connection:
            result = connection.execute(
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
                print(f"Name: {row[0]}, Avg: {row[1]:.2f}, Count: {row[2]}, First: {row[3]}, Last: {row[4]}")

        # Convert to pandas DataFrame
        df = pd.read_sql("SELECT * FROM test_table ORDER BY id", engine)
        print("\nDataFrame:")
        print(df)

        # Create and query a view
        create_view_sql = """
        CREATE OR REPLACE VIEW test_view AS
        SELECT
            name,
            AVG(value) as avg_value,
            COUNT(*) as count
        FROM test_table
        GROUP BY name
        """

        with engine.begin() as connection:
            connection.execute(text(create_view_sql))
            print("\nCreated view")

            result = connection.execute(text("SELECT * FROM test_view"))
            print("\nView results:")
            for row in result:
                print(f"Name: {row[0]}, Avg: {row[1]:.2f}, Count: {row[2]}")


if __name__ == "__main__":
    basic_example()
