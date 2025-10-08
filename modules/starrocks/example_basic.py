import pandas as pd
import sqlalchemy
from sqlalchemy import text

from testcontainers.starrocks import StarRocksContainer

from datetime import datetime

def basic_example():
    with StarRocksContainer() as starrocks:
        # Get connection URL
        connection_url = starrocks.get_connection_url()

        # Create SQLAlchemy engine
        engine = sqlalchemy.create_engine(connection_url)
        print("Connected to StarRocks")

        # Create a test table
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS weatherdata (
                DATE DATETIME,
                NAME STRING,
                Temperature STRING
            )
            ENGINE=olap
            DUPLICATE KEY(DATE)
            DISTRIBUTED BY HASH(DATE) BUCKETS 10;
        """

        with engine.begin() as connection:
            connection.execute(text(create_table_sql))
            print("Created test table")

        # Insert test data
        test_data = test_data = [
                {"date": datetime(2025, 1, 1, 10, 0), "name": "New York", "temperature": "25°C"},
                {"date": datetime(2025, 1, 2, 10, 0), "name": "London", "temperature": "15°C"},
                {"date": datetime(2025, 1, 3, 10, 0), "name": "Tokyo", "temperature": "20°C"},
                {"date": datetime(2025, 1, 4, 10, 0), "name": "Sydney", "temperature": "30°C"},
                {"date": datetime(2025, 1, 5, 10, 0), "name": "Paris", "temperature": "18°C"},
                {"date": datetime(2025, 1, 6, 10, 0), "name": "Berlin", "temperature": "16°C"},
                {"date": datetime(2025, 1, 7, 10, 0), "name": "Moscow", "temperature": "5°C"},
                {"date": datetime(2025, 1, 8, 10, 0), "name": "Dubai", "temperature": "35°C"},
                {"date": datetime(2025, 1, 9, 10, 0), "name": "Singapore", "temperature": "28°C"},
                {"date": datetime(2025, 1, 10, 10, 0), "name": "Toronto", "temperature": "10°C"},
            ]

        with engine.begin() as connection:
            for data in test_data:
                connection.execute(text("INSERT INTO weatherdata (DATE, NAME, Temperature) VALUES (:date, :name, :temperature)"), data)
            print("Inserted test data")
        
        # Query data
        with engine.connect() as connection:
            try:
                result = connection.execute(text("SELECT * FROM weatherdata ORDER BY DATE"))
                rows = result.fetchall()

                print("\nQuery results:")
                for row in rows:
                    print(f"Date: {row[0]}, City: {row[1]}, Temperature: {row[2]}")
            except sqlalchemy.exc.ProgrammingError as e:
                print(f"Error querying data: {e}")
        
        # Execute a more complex query
        with engine.connect() as connection:
            try:
                result = connection.execute(
                    text("""
                        SELECT
                            NAME,
                            AVG(CAST(REGEXP_REPLACE(Temperature, '[^0-9.]', '') AS FLOAT)) as avg_temperature,
                            COUNT(*) as count,
                            MIN(DATE) as first_date,
                            MAX(DATE) as last_date
                        FROM weatherdata
                        GROUP BY NAME
                        ORDER BY avg_temperature DESC
                    """)
                )

                print("\nAggregation results:")
                for row in result:
                    print(f"City: {row[0]}, Avg Temperature: {row[1]:.2f}°C, Count: {row[2]}, First: {row[3]}, Last: {row[4]}")
            except sqlalchemy.exc.ProgrammingError as e:
                print(f"Error executing query: {e}")


if __name__ == "__main__":
    basic_example()
