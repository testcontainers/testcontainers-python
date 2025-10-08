import logging
from typing import Any, Optional
from urllib.parse import quote, urlencode

from testcontainers.core.container import DockerContainer
from testcontainers.core.exceptions import ContainerStartException
from testcontainers.core.waiting_utils import WaitStrategy

logger = logging.getLogger(__name__)


class SqlContainer(DockerContainer):
    """
    Generic SQL database container providing common functionality.

    This class can serve as a base for database-specific container implementations.
    It provides connection management, URL construction, and basic lifecycle methods.
    Database connection readiness is automatically handled by the provided wait strategy.

    Note: `SqlAlchemyConnectWaitStrategy` from `sql_connection_wait_strategy` is a provided wait strategy for SQL databases.
    """

    def __init__(self, image: str, wait_strategy: WaitStrategy, **kwargs):
        """
        Initialize SqlContainer with optional wait strategy.

        Args:
            image: Docker image name
            wait_strategy: Wait strategy for SQL database connectivity
            **kwargs: Additional arguments passed to DockerContainer
        """
        super().__init__(image, **kwargs)
        self.wait_strategy = wait_strategy

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

        if self._container is None:
            raise ContainerStartException("Container has not been started")

        host = host or self.get_container_host_ip()
        exposed_port = self.get_exposed_port(port)
        quoted_password = quote(password, safe="")
        quoted_username = quote(username, safe="")
        url = f"{dialect}://{quoted_username}:{quoted_password}@{host}:{exposed_port}"

        if dbname:
            quoted_dbname = quote(dbname, safe="")
            url = f"{url}/{quoted_dbname}"

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
            self.waiting_for(self.wait_strategy)
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
