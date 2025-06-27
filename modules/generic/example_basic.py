import requests

from testcontainers.generic import GenericContainer


def basic_example():
    # Example 1: Nginx container
    with GenericContainer("nginx:latest") as nginx:
        # Get connection parameters
        host = nginx.get_container_host_ip()
        port = nginx.get_exposed_port(80)

        # Test Nginx
        response = requests.get(f"http://{host}:{port}")
        print("\nNginx response:")
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")

    # Example 2: Redis container with custom configuration
    with GenericContainer("redis:latest") as redis:
        # Get connection parameters
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(6379)

        # Test Redis
        import redis

        r = redis.Redis(host=host, port=port)
        r.set("test_key", "Hello, Redis!")
        value = r.get("test_key")
        print("\nRedis test:")
        print(f"Retrieved value: {value.decode()}")

    # Example 3: PostgreSQL container with environment variables
    with GenericContainer(
        "postgres:latest",
        environment={"POSTGRES_USER": "testuser", "POSTGRES_PASSWORD": "testpass", "POSTGRES_DB": "testdb"},
    ) as postgres:
        # Get connection parameters
        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(5432)

        # Test PostgreSQL
        import psycopg2

        conn = psycopg2.connect(host=host, port=port, user="testuser", password="testpass", database="testdb")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print("\nPostgreSQL test:")
        print(f"Version: {version[0]}")
        cur.close()
        conn.close()

    # Example 4: Custom container with volume mounting
    with GenericContainer("python:3.9-slim", volumes={"/tmp/test": {"bind": "/app", "mode": "rw"}}) as python:
        # Get container ID
        container_id = python.get_container_id()
        print(f"\nPython container ID: {container_id}")

        # Execute command in container
        exit_code, output = python.exec_run("python -c 'print(\"Hello from container!\")'")
        print(f"Command output: {output.decode()}")

    # Example 5: Container with health check
    with GenericContainer(
        "mongo:latest",
        healthcheck={
            "test": ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"],
            "interval": 1000000000,  # 1 second
            "timeout": 3000000000,  # 3 seconds
            "retries": 3,
        },
    ) as mongo:
        # Get connection parameters
        host = mongo.get_container_host_ip()
        port = mongo.get_exposed_port(27017)

        # Test MongoDB
        from pymongo import MongoClient

        client = MongoClient(f"mongodb://{host}:{port}")
        db = client.test_db
        collection = db.test_collection
        collection.insert_one({"test": "Hello, MongoDB!"})
        result = collection.find_one()
        print("\nMongoDB test:")
        print(f"Retrieved document: {result}")

    # Example 6: Container with network
    with GenericContainer("nginx:latest", network="test_network") as nginx_network:
        # Get network info
        network_info = nginx_network.get_network_info()
        print("\nNetwork test:")
        print(f"Network name: {network_info['Name']}")
        print(f"Network ID: {network_info['Id']}")

    # Example 7: Container with resource limits
    with GenericContainer("nginx:latest", mem_limit="512m", cpu_period=100000, cpu_quota=50000) as nginx_limits:
        # Get container stats
        stats = nginx_limits.get_stats()
        print("\nResource limits test:")
        print(f"Memory limit: {stats['memory_stats']['limit']}")
        print(f"CPU usage: {stats['cpu_stats']['cpu_usage']['total_usage']}")

    # Example 8: Container with custom command
    with GenericContainer("python:3.9-slim", command=["python", "-c", "print('Custom command test')"]) as python_cmd:
        # Get logs
        logs = python_cmd.get_logs()
        print("\nCustom command test:")
        print(f"Container logs: {logs.decode()}")


if __name__ == "__main__":
    basic_example()
