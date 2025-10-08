import pytest
from unittest.mock import patch

from testcontainers.core.exceptions import ContainerStartException
from testcontainers.generic.sql import SqlContainer
from testcontainers.generic.providers.sql_connection_wait_strategy import SqlConnectWaitStrategy


class SimpleSqlContainer(SqlContainer):
    """Simple concrete implementation for testing."""

    def __init__(self, image: str = "postgres:13"):
        super().__init__(image, wait_strategy=SqlConnectWaitStrategy())
        self.username = "testuser"
        self.password = "testpass"
        self.dbname = "testdb"
        self.port = 5432

    def get_connection_url(self) -> str:
        return self._create_connection_url(
            dialect="postgresql", username=self.username, password=self.password, port=self.port, dbname=self.dbname
        )

    def _configure(self) -> None:
        self.with_env("POSTGRES_USER", self.username)
        self.with_env("POSTGRES_PASSWORD", self.password)
        self.with_env("POSTGRES_DB", self.dbname)
        self.with_exposed_ports(self.port)


class TestSqlContainer:
    def test_abstract_methods_raise_not_implemented(self):
        container = SqlContainer("test:latest", SqlConnectWaitStrategy())

        with pytest.raises(NotImplementedError):
            container.get_connection_url()

        with pytest.raises(NotImplementedError):
            container._configure()

    def test_transfer_seed_default_behavior(self):
        container = SqlContainer("test:latest", SqlConnectWaitStrategy())
        # Should not raise an exception
        container._transfer_seed()

    def test_connection_url_creation_basic(self):
        container = SimpleSqlContainer()
        container._container = type("MockContainer", (), {})()  # Simple mock
        container.get_container_host_ip = lambda: "localhost"
        container.get_exposed_port = lambda port: port

        url = container._create_connection_url(dialect="postgresql", username="user", password="pass", port=5432)

        assert url == "postgresql://user:pass@localhost:5432"

    def test_connection_url_with_database_name(self):
        container = SimpleSqlContainer()
        container._container = type("MockContainer", (), {})()
        container.get_container_host_ip = lambda: "localhost"
        container.get_exposed_port = lambda port: port

        url = container._create_connection_url(
            dialect="postgresql", username="user", password="pass", port=5432, dbname="mydb"
        )

        assert url == "postgresql://user:pass@localhost:5432/mydb"

    def test_connection_url_with_special_characters(self):
        container = SimpleSqlContainer()
        container._container = type("MockContainer", (), {})()
        container.get_container_host_ip = lambda: "localhost"
        container.get_exposed_port = lambda port: port

        url = container._create_connection_url(
            dialect="postgresql", username="user@domain", password="p@ss/word", port=5432
        )

        # Check that special characters are URL encoded
        assert "user%40domain" in url
        assert "p%40ss%2Fword" in url

    def test_connection_url_with_query_params(self):
        container = SimpleSqlContainer()
        container._container = type("MockContainer", (), {})()
        container.get_container_host_ip = lambda: "localhost"
        container.get_exposed_port = lambda port: port

        url = container._create_connection_url(
            dialect="postgresql",
            username="user",
            password="pass",
            port=5432,
            query_params={"ssl": "require", "timeout": "30"},
        )

        assert "?" in url
        assert "ssl=require" in url
        assert "timeout=30" in url

    def test_connection_url_type_errors(self):
        """Test that _create_connection_url raises TypeError with invalid types"""
        container = SimpleSqlContainer()
        container._container = type("MockContainer", (), {"id": "test-id"})()

        # Mock get_exposed_port to simulate what happens with None port
        with patch.object(container, "get_exposed_port") as mock_get_port:
            # Simulate the TypeError that would occur when int(None) is called
            mock_get_port.side_effect = TypeError(
                "int() argument must be a string, a bytes-like object or a real number, not 'NoneType'"
            )

            with pytest.raises(TypeError, match="int\\(\\) argument must be a string"):
                container._create_connection_url("postgresql", "user", "pass", port=None)

    def test_connection_url_container_not_started(self):
        container = SimpleSqlContainer()
        container._container = None

        with pytest.raises(ContainerStartException, match="Container has not been started"):
            container._create_connection_url("postgresql", "user", "pass", port=5432)

    def test_container_configuration(self):
        container = SimpleSqlContainer("postgres:13")

        # Test that configuration sets up environment
        container._configure()

        assert container.env["POSTGRES_USER"] == "testuser"
        assert container.env["POSTGRES_PASSWORD"] == "testpass"
        assert container.env["POSTGRES_DB"] == "testdb"

    def test_concrete_container_connection_url(self):
        container = SimpleSqlContainer()
        container._container = type("MockContainer", (), {})()
        container.get_container_host_ip = lambda: "localhost"
        container.get_exposed_port = lambda port: 5432

        url = container.get_connection_url()

        assert url.startswith("postgresql://")
        assert "testuser" in url
        assert "testpass" in url
        assert "testdb" in url
        assert "localhost:5432" in url

    def test_container_inheritance(self):
        container = SimpleSqlContainer()

        assert isinstance(container, SqlContainer)
        assert hasattr(container, "get_connection_url")
        assert hasattr(container, "_configure")
        assert hasattr(container, "_transfer_seed")
        assert hasattr(container, "start")

    def test_additional_transient_errors_list(self):
        from testcontainers.generic.providers.sql_connection_wait_strategy import ADDITIONAL_TRANSIENT_ERRORS

        assert isinstance(ADDITIONAL_TRANSIENT_ERRORS, list)
        # List may be empty if SQLAlchemy not available, or contain DBAPIError if it is

    def test_empty_password_handling(self):
        container = SimpleSqlContainer()
        container._container = type("MockContainer", (), {})()
        container.get_container_host_ip = lambda: "localhost"
        container.get_exposed_port = lambda port: port

        url = container._create_connection_url(dialect="postgresql", username="user", password="", port=5432)

        assert url == "postgresql://user:@localhost:5432"

    def test_unicode_characters_in_credentials(self):
        container = SimpleSqlContainer()
        container._container = type("MockContainer", (), {})()
        container.get_container_host_ip = lambda: "localhost"
        container.get_exposed_port = lambda port: port

        url = container._create_connection_url(
            dialect="postgresql", username="usér", password="päss", port=5432, dbname="tëstdb"
        )

        assert "us%C3%A9r" in url
        assert "p%C3%A4ss" in url
        assert "t%C3%ABstdb" in url

    def test_start_postgres_container_integration(self):
        """Integration test that actually starts a PostgreSQL container."""
        container = SimpleSqlContainer()

        # This will start the container and test the connection
        container.start()

        # Verify the container is running
        assert container._container is not None

        # Test that we can get a connection URL
        url = container.get_connection_url()
        assert url.startswith("postgresql://")
        assert "testuser" in url
        assert "testdb" in url

        # Verify environment variables are set
        assert container.env["POSTGRES_USER"] == "testuser"
        assert container.env["POSTGRES_PASSWORD"] == "testpass"
        assert container.env["POSTGRES_DB"] == "testdb"

        # check logs
        logs = container.get_logs()
        assert "database system is ready to accept connections" in logs[0].decode("utf-8").lower()

    def test_sql_postgres_container_integration(self):
        """Integration test for SqlContainer with PostgreSQL."""
        container = SimpleSqlContainer()

        # This will start the container and test the connection
        container.start()

        # Verify the container is running
        assert container._container is not None

        # Test that we can get a connection URL
        url = container.get_connection_url()

        # check sql operations
        import sqlalchemy

        engine = sqlalchemy.create_engine(url)
        with engine.connect() as conn:
            # Create a test table
            conn.execute(
                sqlalchemy.text("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name VARCHAR(50));")
            )
            # Insert a test record
            conn.execute(sqlalchemy.text("INSERT INTO test_table (name) VALUES ('test_name');"))
            # Query the test record
            result = conn.execute(sqlalchemy.text("SELECT name FROM test_table WHERE name='test_name';"))
            fetched = result.fetchone()
            assert fetched is not None
            assert fetched[0] == "test_name"
