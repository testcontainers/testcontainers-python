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
SQL_TRANSIENT_EXCEPTIONS = (TimeoutError, ConnectionError, *ADDITIONAL_TRANSIENT_ERRORS)


class ConnectWaitStrategy(WaitStrategy):
    """
    Wait strategy that tests database connectivity until it succeeds or times out.

    This strategy performs database connection testing using SQLAlchemy directly,
    handling transient connection errors and providing appropriate retry logic
    for database connectivity testing.
    """

    def __init__(self, transient_exceptions: Optional[tuple] = None):
        super().__init__()
        self.transient_exceptions = transient_exceptions or (TimeoutError, ConnectionError)

    def wait_until_ready(self, container: WaitStrategyTarget) -> None:
        """
        Test database connectivity with retry logic until it succeeds or times out.

        Args:
            container: The SQL container that must have get_connection_url method

        Raises:
            TimeoutError: If connection fails after timeout
            AttributeError: If container doesn't have get_connection_url method
            ImportError: If SQLAlchemy is not installed
            Exception: Any non-transient errors from connection attempts
        """
        import time

        if not hasattr(container, "get_connection_url"):
            raise AttributeError(f"Container {container} must have a get_connection_url method")

        try:
            import sqlalchemy
        except ImportError as e:
            logger.error("SQLAlchemy is required for database connectivity testing")
            raise ImportError("SQLAlchemy is required for database containers") from e

        start_time = time.time()

        while True:
            if time.time() - start_time > self._startup_timeout:
                raise TimeoutError(
                    f"Database connection failed after {self._startup_timeout}s timeout. "
                    f"Hint: Check if the container is ready and the database is accessible."
                )

            try:
                connection_url = container.get_connection_url()
                engine = sqlalchemy.create_engine(connection_url)

                try:
                    with engine.connect():
                        logger.info("Database connection test successful")
                        return
                except Exception as e:
                    logger.debug(f"Database connection attempt failed: {e}")
                    raise
                finally:
                    engine.dispose()

            except self.transient_exceptions as e:
                logger.debug(f"Connection attempt failed: {e}, retrying in {self._poll_interval}s...")
            except Exception as e:
                logger.error(f"Connection failed with non-transient error: {e}")
                raise

            time.sleep(self._poll_interval)


class SqlContainer(DockerContainer):
    """
    Generic SQL database container providing common functionality.

    This class can serve as a base for database-specific container implementations.
    It provides connection management, URL construction, and basic lifecycle methods.
    Database connection readiness is automatically handled by ConnectWaitStrategy.
    """

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
            self.waiting_for(ConnectWaitStrategy(SQL_TRANSIENT_EXCEPTIONS))
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
