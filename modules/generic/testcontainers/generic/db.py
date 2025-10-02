#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import logging
from typing import Any, Optional
from urllib.parse import quote, urlencode

from testcontainers.core.container import DockerContainer
from testcontainers.core.exceptions import ContainerStartException
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready

logger = logging.getLogger(__name__)

ADDITIONAL_TRANSIENT_ERRORS = []
try:
    from sqlalchemy.exc import DBAPIError

    ADDITIONAL_TRANSIENT_ERRORS.append(DBAPIError)
except ImportError:
    logger.debug("SQLAlchemy not available, skipping DBAPIError handling")


class DbContainer(DockerContainer):
    """
    Generic database container providing common database functionality.

    This class serves as a base for database-specific container implementations.
    It provides connection management, URL construction, and basic lifecycle methods.

    Note:
        This class is deprecated and will be removed in a future version.
        Use database-specific container classes instead.
    """

    @wait_container_is_ready(*ADDITIONAL_TRANSIENT_ERRORS)
    def _connect(self) -> None:
        """
        Test database connectivity using SQLAlchemy.

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
        logger.debug(f"Testing database connection to {self._mask_password_in_url(connection_url)}")

        engine = sqlalchemy.create_engine(connection_url)
        try:
            with engine.connect():
                logger.info("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
        finally:
            engine.dispose()

    def get_connection_url(self) -> str:
        """
        Get the database connection URL.

        Returns:
            str: Database connection URL

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement get_connection_url()")

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

        logger.debug(f"Created connection URL: {self._mask_password_in_url(url)}")
        return url

    def _mask_password_in_url(self, url: str) -> str:
        """
        Mask password in URL for safe logging.

        Args:
            url: Database connection URL

        Returns:
            str: URL with masked password
        """
        try:
            # Simple regex-based masking for logging
            import re

            return re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", url)
        except Exception:
            return "[URL with masked credentials]"

    def start(self) -> "DbContainer":
        """
        Start the database container and perform initialization.

        Returns:
            DbContainer: Self for method chaining

        Raises:
            ContainerStartException: If container fails to start
            Exception: If configuration, seed transfer, or connection fails
        """
        logger.info(f"Starting database container: {self.image}")

        try:
            self._configure()
            super().start()
            self._transfer_seed()
            self._connect()
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
