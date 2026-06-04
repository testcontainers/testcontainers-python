import ibm_db
import ibm_db_dbi
import pandas as pd

from testcontainers.db2 import Db2Container


def basic_example():
    with Db2Container() as db2:
        # Get connection parameters
        host = db2.get_container_host_ip()
        port = db2.get_exposed_port(db2.port)
        database = db2.database
        username = db2.username
        password = db2.password

        # Create connection string
        conn_str = f"DATABASE={database};HOSTNAME={host};PORT={port};PROTOCOL=TCPIP;UID={username};PWD={password}"

        # Connect to DB2
        conn = ibm_db.connect(conn_str, "", "")
        print("Connected to DB2")

        # Create a test table
        create_table_sql = """
        CREATE TABLE test_table (
            id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(50),
            value DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT TIMESTAMP
        )
        """

        try:
            ibm_db.exec_immediate(conn, create_table_sql)
            print("Created test table")
        except Exception as e:
            print(f"Table might already exist: {e}")

        # Insert test data
        test_data = [(1, "test1", 100.0), (2, "test2", 200.0), (3, "test3", 300.0)]

        insert_sql = "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)"
        stmt = ibm_db.prepare(conn, insert_sql)

        for row in test_data:
            ibm_db.execute(stmt, row)
        print("Inserted test data")

        # Query data using ibm_db_dbi
        conn_dbi = ibm_db_dbi.Connection(conn)
        cursor = conn_dbi.cursor()

        cursor.execute("SELECT * FROM test_table ORDER BY id")
        rows = cursor.fetchall()

        print("\nQuery results:")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Value: {row[2]}, Created: {row[3]}")

        # Execute a more complex query
        cursor.execute("""
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

        print("\nAggregation results:")
        for row in cursor.fetchall():
            print(f"Name: {row[0]}, Avg: {row[1]:.2f}, Count: {row[2]}, First: {row[3]}, Last: {row[4]}")

        # Convert to pandas DataFrame
        df = pd.read_sql("SELECT * FROM test_table ORDER BY id", conn_dbi)
        print("\nDataFrame:")
        print(df)

        # Clean up
        cursor.close()
        ibm_db.close(conn)


if __name__ == "__main__":
    basic_example()
