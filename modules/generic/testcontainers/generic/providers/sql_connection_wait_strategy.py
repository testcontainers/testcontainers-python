# This module provides a wait strategy for SQL database connectivity testing using SQLAlchemy.
# It includes handling for transient exceptions and connection retries.

import logging

from testcontainers.core.waiting_utils import WaitStrategy, WaitStrategyTarget

logger = logging.getLogger(__name__)

ADDITIONAL_TRANSIENT_ERRORS = []
try:
    from sqlalchemy.exc import DBAPIError

    ADDITIONAL_TRANSIENT_ERRORS.append(DBAPIError)
except ImportError:
    logger.debug("SQLAlchemy not available, skipping DBAPIError handling")


class SqlAlchemyConnectWaitStrategy(WaitStrategy):
    """Wait strategy for database connectivity testing using SQLAlchemy."""

    def __init__(self):
        super().__init__()
        self.with_transient_exceptions(TimeoutError, ConnectionError, *ADDITIONAL_TRANSIENT_ERRORS)

    def wait_until_ready(self, container: WaitStrategyTarget) -> None:
        """Test database connectivity with retry logic until success or timeout."""
        if not hasattr(container, "get_connection_url"):
            raise AttributeError(f"Container {container} must have a get_connection_url method")

        try:
            import sqlalchemy
        except ImportError as e:
            raise ImportError("SQLAlchemy is required for database containers") from e

        def _test_connection() -> bool:
            """Test database connection, returning True if successful."""
            engine = sqlalchemy.create_engine(container.get_connection_url())
            try:
                with engine.connect():
                    logger.info("Database connection successful")
                    return True
            finally:
                engine.dispose()

        result = self._poll(_test_connection)
        if not result:
            raise TimeoutError(f"Database connection failed after {self._startup_timeout}s timeout")
