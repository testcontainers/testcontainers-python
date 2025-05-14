import pyodbc

from testcontainers.mssql import MsSqlContainer


def basic_example():
    with MsSqlContainer() as mssql:
        # Get connection parameters
        host = mssql.get_container_host_ip()
        port = mssql.get_exposed_port(mssql.port)
        username = mssql.username
        password = mssql.password
        database = mssql.database

        # Create connection string
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host},{port};DATABASE={database};UID={username};PWD={password}"

        # Connect to MSSQL
        connection = pyodbc.connect(conn_str)
        print("Connected to MSSQL")

        # Create cursor
        cursor = connection.cursor()

        # Create test table
        cursor.execute("""
            CREATE TABLE test_table (
                id INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(50),
                value INT,
                category NVARCHAR(10),
                created_at DATETIME2 DEFAULT GETDATE()
            )
        """)
        print("Created test table")

        # Insert test data
        test_data = [("test1", 100, "A"), ("test2", 200, "B"), ("test3", 300, "A")]

        cursor.executemany(
            """
            INSERT INTO test_table (name, value, category)
            VALUES (?, ?, ?)
        """,
            test_data,
        )
        print("Inserted test data")

        # Commit changes
        connection.commit()

        # Query data
        print("\nQuery results:")
        cursor.execute("SELECT * FROM test_table WHERE category = 'A'")
        for row in cursor:
            print({"id": row[0], "name": row[1], "value": row[2], "category": row[3], "created_at": row[4].isoformat()})

        # Create view
        cursor.execute("""
            CREATE OR ALTER VIEW test_view AS
            SELECT category, COUNT(*) as count, AVG(value) as avg_value
            FROM test_table
            GROUP BY category
        """)
        print("\nCreated view")

        # Query view
        print("\nView results:")
        cursor.execute("SELECT * FROM test_view")
        for row in cursor:
            print({"category": row[0], "count": row[1], "avg_value": float(row[2])})

        # Create index
        cursor.execute("CREATE INDEX test_idx ON test_table (value)")
        print("\nCreated index")

        # Query using index
        print("\nQuery using index:")
        cursor.execute("SELECT * FROM test_table WHERE value > 150")
        for row in cursor:
            print({"id": row[0], "name": row[1], "value": row[2], "category": row[3], "created_at": row[4].isoformat()})

        # Get table metadata
        cursor.execute("""
            SELECT
                c.name as column_name,
                t.name as data_type,
                c.max_length,
                c.is_nullable
            FROM sys.columns c
            JOIN sys.types t ON c.user_type_id = t.user_type_id
            WHERE OBJECT_ID = OBJECT_ID('test_table')
            ORDER BY c.column_id
        """)
        print("\nTable metadata:")
        for row in cursor:
            print({"column": row[0], "type": row[1], "length": row[2], "nullable": row[3]})

        # Create stored procedure
        cursor.execute("""
            CREATE OR ALTER PROCEDURE test_proc
                @category NVARCHAR(10),
                @count INT OUTPUT
            AS
            BEGIN
                SELECT @count = COUNT(*)
                FROM test_table
                WHERE category = @category
            END
        """)
        print("\nCreated stored procedure")

        # Execute stored procedure
        cursor.execute("""
            DECLARE @count INT
            EXEC test_proc @category = 'A', @count = @count OUTPUT
            SELECT @count as count
        """)
        count = cursor.fetchone()[0]
        print(f"Count for category A: {count}")

        # Create function
        cursor.execute("""
            CREATE OR ALTER FUNCTION test_func(@category NVARCHAR(10))
            RETURNS TABLE
            AS
            RETURN
            (
                SELECT name, value
                FROM test_table
                WHERE category = @category
            )
        """)
        print("\nCreated function")

        # Use function
        print("\nFunction results:")
        cursor.execute("SELECT * FROM test_func('A')")
        for row in cursor:
            print({"name": row[0], "value": row[1]})

        # Create trigger
        cursor.execute("""
            CREATE OR ALTER TRIGGER test_trigger
            ON test_table
            AFTER INSERT
            AS
            BEGIN
                PRINT 'New row inserted'
            END
        """)
        print("\nCreated trigger")

        # Test trigger
        cursor.execute("INSERT INTO test_table (name, value, category) VALUES ('test4', 400, 'B')")
        connection.commit()

        # Clean up
        cursor.close()
        connection.close()


if __name__ == "__main__":
    basic_example()
