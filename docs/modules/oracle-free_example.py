import oracledb

from testcontainers.oracle_free import OracleFreeContainer


def basic_example():
    with OracleFreeContainer() as oracle:
        # Get connection parameters
        host = oracle.get_container_host_ip()
        port = oracle.get_exposed_port(oracle.port)
        username = oracle.username
        password = oracle.password
        service_name = oracle.service_name

        # Create connection string
        dsn = f"{host}:{port}/{service_name}"

        # Connect to Oracle
        connection = oracledb.connect(user=username, password=password, dsn=dsn)
        print("Connected to Oracle")

        # Create cursor
        cursor = connection.cursor()

        # Create test table
        cursor.execute("""
            CREATE TABLE test_table (
                id NUMBER GENERATED ALWAYS AS IDENTITY,
                name VARCHAR2(50),
                value NUMBER,
                category VARCHAR2(10),
                created_at TIMESTAMP DEFAULT SYSTIMESTAMP
            )
        """)
        print("Created test table")

        # Insert test data
        test_data = [("test1", 100, "A"), ("test2", 200, "B"), ("test3", 300, "A")]

        cursor.executemany(
            """
            INSERT INTO test_table (name, value, category)
            VALUES (:1, :2, :3)
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
            CREATE OR REPLACE VIEW test_view AS
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
            SELECT column_name, data_type, data_length, nullable
            FROM user_tab_columns
            WHERE table_name = 'TEST_TABLE'
            ORDER BY column_id
        """)
        print("\nTable metadata:")
        for row in cursor:
            print({"column": row[0], "type": row[1], "length": row[2], "nullable": row[3]})

        # Create sequence
        cursor.execute("""
            CREATE SEQUENCE test_seq
            START WITH 1
            INCREMENT BY 1
            NOCACHE
            NOCYCLE
        """)
        print("\nCreated sequence")

        # Use sequence
        cursor.execute("SELECT test_seq.NEXTVAL FROM DUAL")
        next_val = cursor.fetchone()[0]
        print(f"Next sequence value: {next_val}")

        # Create procedure
        cursor.execute("""
            CREATE OR REPLACE PROCEDURE test_proc (
                p_category IN VARCHAR2,
                p_count OUT NUMBER
            ) AS
            BEGIN
                SELECT COUNT(*)
                INTO p_count
                FROM test_table
                WHERE category = p_category;
            END;
        """)
        print("\nCreated procedure")

        # Execute procedure
        cursor.execute("""
            DECLARE
                v_count NUMBER;
            BEGIN
                test_proc('A', v_count);
                DBMS_OUTPUT.PUT_LINE('Count for category A: ' || v_count);
            END;
        """)

        # Clean up
        cursor.close()
        connection.close()


if __name__ == "__main__":
    basic_example()
