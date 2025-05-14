import sqlalchemy

from testcontainers.mssql import SqlServerContainer


def basic_example():
    # Create a SQL Server container with default settings
    with SqlServerContainer() as mssql:
        # Get the connection URL
        connection_url = mssql.get_connection_url()
        print(f"Connection URL: {connection_url}")

        # Create a SQLAlchemy engine
        engine = sqlalchemy.create_engine(connection_url)

        # Create a test table and insert some data
        with engine.begin() as connection:
            # Create a test table
            connection.execute(
                sqlalchemy.text("""
                CREATE TABLE test_table (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    name NVARCHAR(50),
                    value INT
                )
            """)
            )
            print("Created test table")

            # Insert some test data
            connection.execute(
                sqlalchemy.text("""
                INSERT INTO test_table (name, value)
                VALUES
                    ('test1', 100),
                    ('test2', 200),
                    ('test3', 300)
            """)
            )
            print("Inserted test data")

            # Query the data
            result = connection.execute(sqlalchemy.text("SELECT * FROM test_table"))
            print("\nQuery results:")
            for row in result:
                print(f"id: {row[0]}, name: {row[1]}, value: {row[2]}")


if __name__ == "__main__":
    basic_example()
