import logging

from testcontainers.core.waiting_utils import WaitStrategy, WaitStrategyTarget

logger = logging.getLogger(__name__)

ADDITIONAL_TRANSIENT_ERRORS = []
try:
    from sqlalchemy.exc import DBAPIError

    ADDITIONAL_TRANSIENT_ERRORS.append(DBAPIError)
except ImportError:
    logger.debug("SQLAlchemy not available, skipping DBAPIError handling")


class SqlConnectWaitStrategy(WaitStrategy):
    """
    Wait strategy that tests database connectivity until it succeeds or times out.

    This strategy performs database connection testing using SQLAlchemy directly,
    handling transient connection errors and providing appropriate retry logic
    for database connectivity testing.
    """

    def __init__(self):
        super().__init__()
        self.transient_exceptions = (TimeoutError, ConnectionError, *ADDITIONAL_TRANSIENT_ERRORS)

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
