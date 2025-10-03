import logging
from typing import Any, Optional
from urllib.parse import quote, urlencode

from testcontainers.core.container import DockerContainer
from testcontainers.core.exceptions import ContainerStartException
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import WaitStrategy, WaitStrategyTarget

logger = logging.getLogger(__name__)

ADDITIONAL_TRANSIENT_ERRORS = []
try:
    from sqlalchemy.exc import DBAPIError

    ADDITIONAL_TRANSIENT_ERRORS.append(DBAPIError)
except ImportError:
    logger.debug("SQLAlchemy not available, skipping DBAPIError handling")


class DatabaseConnectionWaitStrategy(WaitStrategy):
    """
    Wait strategy for database connection readiness using SqlContainer._connect().

    This strategy implements retry logic and calls SqlContainer._connect()
    repeatedly until it succeeds or times out.
    """

    def __init__(self, sql_container: "SqlContainer"):
        super().__init__()
        self.sql_container = sql_container

    def wait_until_ready(self, container: WaitStrategyTarget) -> None:
        """
        Test database connectivity with retry logic by calling SqlContainer._connect().

        Raises:
            TimeoutError: If connection fails after timeout
            Exception: Any non-transient errors from _connect()
        """
        import time

        start_time = time.time()

        transient_exceptions = (TimeoutError, ConnectionError, *ADDITIONAL_TRANSIENT_ERRORS)

        while True:
            if time.time() - start_time > self._startup_timeout:
                raise TimeoutError(
                    f"Database connection failed after {self._startup_timeout}s timeout. "
                    f"Hint: Check if the database container is ready and accessible."
                )

            try:
                self.sql_container._connect()
                return
            except transient_exceptions as e:
                logger.debug(f"Database connection attempt failed: {e}, retrying in {self._poll_interval}s...")
            except Exception as e:
                logger.error(f"Database connection test failed with non-transient error: {e}")
                raise

            time.sleep(self._poll_interval)


class SqlContainer(DockerContainer):
    """
    Generic SQL database container providing common functionality.

    This class can serve as a base for database-specific container implementations.
    It provides connection management, URL construction, and basic lifecycle methods.
    Database connection readiness is automatically handled by DatabaseConnectionWaitStrategy.
    """

    def _connect(self) -> None:
        """
        Test database connectivity using SQLAlchemy.

        This method performs a single connection test without retry logic.
        Retry logic is handled by the DatabaseConnectionWaitStrategy.

        Raises:
            ImportError: If SQLAlchemy is not installed
            Exception: If connection fails
        """
        try:
            import sqlalchemy
        except ImportError as e:
            logger.error("SQLAlchemy is required for database connectivity testing")
            raise ImportError("SQLAlchemy is required for database containers") from e

        connection_url = self.get_connection_url()
        engine = sqlalchemy.create_engine(connection_url)

        try:
            with engine.connect():
                logger.info("Database connection test successful")
        except Exception as e:
            logger.debug(f"Database connection attempt failed: {e}")
            raise
        finally:
            engine.dispose()

    def _create_connection_url(
        self,
        dialect: str,
        username: str,
        password: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        dbname: Optional[str] = None,
        query_params: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Create a database connection URL.

        Args:
            dialect: Database dialect (e.g., 'postgresql', 'mysql')
            username: Database username
            password: Database password
            host: Database host (defaults to container host)
            port: Database port
            dbname: Database name
            query_params: Additional query parameters for the URL
            **kwargs: Additional parameters (checked for deprecated usage)

        Returns:
            str: Formatted database connection URL

        Raises:
            ValueError: If unexpected arguments are provided or required parameters are missing
            ContainerStartException: If container is not started
        """
        if raise_for_deprecated_parameter(kwargs, "db_name", "dbname"):
            raise ValueError(f"Unexpected arguments: {','.join(kwargs)}")

        if self._container is None:
            raise ContainerStartException("Container has not been started")

        # Validate required parameters
        if not dialect:
            raise ValueError("Database dialect is required")
        if not username:
            raise ValueError("Database username is required")
        if port is None:
            raise ValueError("Database port is required")

        host = host or self.get_container_host_ip()
        exposed_port = self.get_exposed_port(port)

        # Safely quote password to handle special characters
        quoted_password = quote(password, safe="")
        quoted_username = quote(username, safe="")

        # Build base URL
        url = f"{dialect}://{quoted_username}:{quoted_password}@{host}:{exposed_port}"

        # Add database name if provided
        if dbname:
            quoted_dbname = quote(dbname, safe="")
            url = f"{url}/{quoted_dbname}"

        # Add query parameters if provided
        if query_params:
            query_string = urlencode(query_params)
            url = f"{url}?{query_string}"

        return url

    def start(self) -> "SqlContainer":
        """
        Start the database container and perform initialization.

        Returns:
            SqlContainer: Self for method chaining

        Raises:
            ContainerStartException: If container fails to start
            Exception: If configuration, seed transfer, or connection fails
        """
        logger.info(f"Starting database container: {self.image}")

        try:
            self._configure()
            # Set up database connection wait strategy before starting
            self.waiting_for(DatabaseConnectionWaitStrategy(self))
            super().start()
            self._transfer_seed()
            logger.info("Database container started successfully")
        except Exception as e:
            logger.error(f"Failed to start database container: {e}")
            raise

        return self

    def _configure(self) -> None:
        """
        Configure the database container before starting.

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _configure()")

    def _transfer_seed(self) -> None:
        """
        Transfer seed data to the database container.

        This method can be overridden by subclasses to provide
        database-specific seeding functionality.
        """
        logger.debug("No seed data to transfer")

    def get_connection_url(self) -> str:
        """
        Get the database connection URL.

        Returns:
            str: Database connection URL

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement get_connection_url()")
