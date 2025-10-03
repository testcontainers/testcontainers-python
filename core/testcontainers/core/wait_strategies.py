"""
Structured wait strategies for containers.

- LogMessageWaitStrategy: Wait for specific log messages
- HttpWaitStrategy: Wait for HTTP endpoints to be available
- HealthcheckWaitStrategy: Wait for Docker health checks to pass
- PortWaitStrategy: Wait for TCP ports to be available
- FileExistsWaitStrategy: Wait for files to exist on the filesystem
- CompositeWaitStrategy: Combine multiple wait strategies

Example:
    Basic usage with containers:

    from testcontainers.core.wait_strategies import HttpWaitStrategy, LogMessageWaitStrategy

    # Wait for HTTP endpoint
    container.waiting_for(HttpWaitStrategy(8080).for_status_code(200))

    # Wait for log message
    container.waiting_for(LogMessageWaitStrategy("Server started"))

    # Combine multiple strategies
    container.waiting_for(CompositeWaitStrategy(
        LogMessageWaitStrategy("Database ready"),
        HttpWaitStrategy(8080)
    ))
"""

import re
import socket
import time
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional, Union, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from typing_extensions import Self

from testcontainers.compose import DockerCompose
from testcontainers.core.utils import setup_logger

# Import base classes from waiting_utils to make them available for tests
from testcontainers.core.waiting_utils import WaitStrategy, WaitStrategyTarget

if TYPE_CHECKING:
    from testcontainers.core.container import DockerContainer

logger = setup_logger(__name__)


class LogMessageWaitStrategy(WaitStrategy):
    """
    Wait for a specific message to appear in the container logs.

    This strategy monitors the container's stdout and stderr streams for a specific
    message or regex pattern. It can be configured to wait for the message to appear
    multiple times or to require the message in both streams.

    Raises error if container exits before message is found.

    Args:
        message: The message or regex pattern to search for in the logs
        times: Number of times the message must appear (default: 1)
        predicate_streams_and: If True, message must appear in both stdout and stderr (default: False)

    Example:
        # Wait for a simple message
        strategy = LogMessageWaitStrategy("ready for start")

        # Wait for a regex pattern
        strategy = LogMessageWaitStrategy(re.compile(r"database.*ready"))

        # Wait for message in both streams
        strategy = LogMessageWaitStrategy("ready", predicate_streams_and=True)
    """

    def __init__(
        self, message: Union[str, re.Pattern[str]], times: int = 1, predicate_streams_and: bool = False
    ) -> None:
        super().__init__()
        self._message = message if isinstance(message, re.Pattern) else re.compile(message, re.MULTILINE)
        self._times = times
        self._predicate_streams_and = predicate_streams_and

    def wait_until_ready(self, container: "WaitStrategyTarget") -> None:
        """
        Wait until the specified message appears in the container logs.

        Args:
            container: The container to monitor

        Raises:
            TimeoutError: If the message doesn't appear within the timeout period
            RuntimeError: If the container exits before the message appears
        """
        from .waiting_utils import _NOT_EXITED_STATUSES, _get_container_logs_for_debugging, _get_container_status_info

        # Implement our own wait logic to avoid recursive calls to wait_for_logs
        wrapped = container.get_wrapped_container()
        start_time = time.time()

        while True:
            duration = time.time() - start_time
            if duration > self._startup_timeout:
                # Get current logs and status for debugging
                stdout_str, stderr_str = _get_container_logs_for_debugging(container)
                status_info = _get_container_status_info(container)

                message_pattern = self._message.pattern if hasattr(self._message, "pattern") else str(self._message)

                raise TimeoutError(
                    f"Container did not emit logs containing '{message_pattern}' within {self._startup_timeout:.3f} seconds. "
                    f"Container status: {status_info['status']}, health: {status_info['health_status']}. "
                    f"Recent stdout: {stdout_str}. "
                    f"Recent stderr: {stderr_str}. "
                    f"Hint: Check if the container is starting correctly, the expected message is being logged, "
                    f"and the log pattern matches what the application actually outputs."
                )

            stdout_bytes, stderr_bytes = container.get_logs()
            stdout = stdout_bytes.decode()
            stderr = stderr_bytes.decode()

            predicate_result = (
                self._message.search(stdout) or self._message.search(stderr)
                if self._predicate_streams_and is False
                else self._message.search(stdout) and self._message.search(stderr)
            )

            if predicate_result:
                return

            # Check if container has exited
            wrapped.reload()
            if wrapped.status not in _NOT_EXITED_STATUSES:
                # Get exit information for better debugging
                status_info = _get_container_status_info(container)

                raise RuntimeError(
                    f"Container exited (status: {status_info['status']}, exit code: {status_info['exit_code']}) "
                    f"before emitting logs containing '{self._message.pattern if hasattr(self._message, 'pattern') else str(self._message)}'. "
                    f"Container error: {status_info['error']}. "
                    f"Hint: Check container logs and ensure the application is configured to start correctly. "
                    f"The application may be crashing or exiting early."
                )

            time.sleep(self._poll_interval)


class HttpWaitStrategy(WaitStrategy):
    """
    Wait for an HTTP endpoint to be available and return expected status code(s).

    This strategy makes HTTP requests to a specified endpoint and waits for it to
    return an acceptable status code. It supports various HTTP methods, headers,
    authentication, and custom response validation.

    Args:
        port: The port number to connect to
        path: The HTTP path to request (default: "/")

    Example:
        # Basic HTTP check
        strategy = HttpWaitStrategy(8080).for_status_code(200)

        # HTTPS with custom path
        strategy = HttpWaitStrategy(443, "/health").using_tls().for_status_code(200)

        # Custom validation
        strategy = HttpWaitStrategy(8080).for_response_predicate(lambda body: "ready" in body)

        # Create from URL
        strategy = HttpWaitStrategy.from_url("https://localhost:8080/api/health")
    """

    def __init__(self, port: int, path: Optional[str] = "/") -> None:
        super().__init__()
        self._port = port
        self._path = "/" if path is None else (path if path.startswith("/") else f"/{path}")
        self._status_codes: set[int] = {200}
        self._status_code_predicate: Optional[Callable[[int], bool]] = None
        self._tls = False
        self._headers: dict[str, str] = {}
        self._basic_auth: Optional[tuple[str, str]] = None
        self._response_predicate: Optional[Callable[[str], bool]] = None
        self._method = "GET"
        self._body: Optional[str] = None
        self._insecure_tls = False

    @classmethod
    def from_url(cls, url: str) -> "HttpWaitStrategy":
        """
        Create an HttpWaitStrategy from a URL string.

        Args:
            url: The URL to wait for (e.g., "http://localhost:8080/api/health")

        Returns:
            An HttpWaitStrategy configured for the given URL

        Example:
            strategy = HttpWaitStrategy.from_url("https://localhost:8080/api/health")
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        path = parsed.path or "/"

        strategy = cls(port, path)

        if parsed.scheme == "https":
            strategy.using_tls()

        return strategy

    def for_status_code(self, code: int) -> "HttpWaitStrategy":
        """
        Add an acceptable status code.

        Args:
            code: HTTP status code to accept

        Returns:
            self for method chaining
        """
        self._status_codes.add(code)
        return self

    def for_status_code_matching(self, predicate: Callable[[int], bool]) -> "HttpWaitStrategy":
        """
        Set a predicate to match status codes against.

        Args:
            predicate: Function that takes a status code and returns True if acceptable

        Returns:
            self for method chaining
        """
        self._status_code_predicate = predicate
        return self

    def for_response_predicate(self, predicate: Callable[[str], bool]) -> "HttpWaitStrategy":
        """
        Set a predicate to match response body against.

        Args:
            predicate: Function that takes response body and returns True if acceptable

        Returns:
            self for method chaining
        """
        self._response_predicate = predicate
        return self

    def using_tls(self, insecure: bool = False) -> "HttpWaitStrategy":
        """
        Use HTTPS instead of HTTP.

        Args:
            insecure: If True, skip SSL certificate verification

        Returns:
            self for method chaining
        """
        self._tls = True
        self._insecure_tls = insecure
        return self

    def with_header(self, name: str, value: str) -> "HttpWaitStrategy":
        """
        Add a header to the request.

        Args:
            name: Header name
            value: Header value

        Returns:
            self for method chaining
        """
        self._headers[name] = value
        return self

    def with_basic_credentials(self, username: str, password: str) -> "HttpWaitStrategy":
        """
        Add basic auth credentials.

        Args:
            username: Basic auth username
            password: Basic auth password

        Returns:
            self for method chaining
        """
        self._basic_auth = (username, password)
        return self

    def with_method(self, method: str) -> "HttpWaitStrategy":
        """
        Set the HTTP method to use.

        Args:
            method: HTTP method (GET, POST, PUT, etc.)

        Returns:
            self for method chaining
        """
        self._method = method.upper()
        return self

    def with_body(self, body: str) -> "HttpWaitStrategy":
        """
        Set the request body.

        Args:
            body: Request body as string

        Returns:
            self for method chaining
        """
        self._body = body
        return self

    def _setup_headers(self) -> dict[str, str]:
        """Set up headers for the HTTP request."""
        import base64

        headers = self._headers.copy()
        if self._basic_auth:
            auth = base64.b64encode(f"{self._basic_auth[0]}:{self._basic_auth[1]}".encode()).decode()
            headers["Authorization"] = f"Basic {auth}"
        return headers

    def _setup_ssl_context(self) -> Optional[Any]:
        """Set up SSL context if needed."""
        import ssl

        if self._tls and self._insecure_tls:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            return ssl_context
        return None

    def _build_url(self, container: WaitStrategyTarget) -> str:
        """Build the URL for the HTTP request."""
        protocol = "https" if self._tls else "http"
        host = container.get_container_host_ip()
        port = int(container.get_exposed_port(self._port))
        return f"{protocol}://{host}:{port}{self._path}"

    def _check_response(self, response: Any, url: str) -> bool:
        """Check if the response is acceptable."""
        status_code = response.status

        # Check status code matches
        if status_code in self._status_codes or (
            self._status_code_predicate and self._status_code_predicate(status_code)
        ):
            # Check response body if needed
            if self._response_predicate is not None:
                body = response.read().decode()
                return self._response_predicate(body)
            return True
        else:
            raise HTTPError(url, status_code, "Unexpected status code", response.headers, None)

    def wait_until_ready(self, container: WaitStrategyTarget) -> None:
        """
        Wait until the HTTP endpoint is ready and returns an acceptable response.

        Args:
            container: The container to monitor

        Raises:
            TimeoutError: If the endpoint doesn't become ready within the timeout period
        """
        start_time = time.time()
        headers = self._setup_headers()
        ssl_context = self._setup_ssl_context()
        url = self._build_url(container)

        while True:
            if time.time() - start_time > self._startup_timeout:
                self._raise_timeout_error(url)

            if self._try_http_request(url, headers, ssl_context):
                return

            time.sleep(self._poll_interval)

    def _raise_timeout_error(self, url: str) -> None:
        """Raise a timeout error with detailed information."""
        raise TimeoutError(
            f"HTTP endpoint not ready within {self._startup_timeout} seconds. "
            f"Endpoint: {url}. "
            f"Method: {self._method}. "
            f"Expected status codes: {self._status_codes}. "
            f"Hint: Check if the service is listening on port {self._port}, "
            f"the endpoint path is correct, and the service is configured to respond to {self._method} requests."
        )

    def _try_http_request(self, url: str, headers: dict[str, str], ssl_context: Any) -> bool:
        """Try to make an HTTP request and return True if successful."""
        try:
            request = Request(
                url,
                headers=headers,
                method=self._method,
                data=self._body.encode() if self._body else None,
            )

            with urlopen(request, timeout=1, context=ssl_context) as response:
                return self._check_response(response, url)

        except (URLError, HTTPError) as e:
            return self._handle_http_error(e)
        except (ConnectionResetError, ConnectionRefusedError, BrokenPipeError, OSError) as e:
            # Handle connection-level errors that can occur during HTTP requests
            logger.debug(f"HTTP connection failed: {e!s}")
            return False

    def _handle_http_error(self, error: Union[URLError, HTTPError]) -> bool:
        """Handle HTTP errors and return True if error is acceptable."""
        if isinstance(error, HTTPError) and (
            error.code in self._status_codes
            or (self._status_code_predicate and self._status_code_predicate(error.code))
        ):
            return True
        logger.debug(f"HTTP request failed: {error!s}")
        return False


class HealthcheckWaitStrategy(WaitStrategy):
    """
    Wait for the container's health check to report as healthy.

    This strategy monitors the container's Docker health check status and waits
    for it to report as "healthy". It requires the container to have a health
    check configured in its Dockerfile or container configuration.

    Example:
        # Wait for container to be healthy
        strategy = HealthcheckWaitStrategy()

        # With custom timeout
        strategy = HealthcheckWaitStrategy().with_startup_timeout(60)

    Note:
        The container must have a HEALTHCHECK instruction in its Dockerfile
        or health check configured during container creation for this strategy
        to work. If no health check is configured, this strategy will raise
        a RuntimeError.
    """

    def __init__(self) -> None:
        super().__init__()

    def wait_until_ready(self, container: WaitStrategyTarget) -> None:
        """
        Wait until the container's health check reports as healthy.

        Args:
            container: The container to monitor

        Raises:
            TimeoutError: If the health check doesn't report healthy within the timeout period
            RuntimeError: If no health check is configured or if the health check reports unhealthy
        """
        start_time = time.time()
        wrapped = container.get_wrapped_container()

        while True:
            if time.time() - start_time > self._startup_timeout:
                wrapped.reload()  # Refresh container state
                health = wrapped.attrs.get("State", {}).get("Health", {})
                status = health.get("Status") if health else "no health check"
                raise TimeoutError(
                    f"Container health check did not report healthy within {self._startup_timeout} seconds. "
                    f"Current status: {status}. "
                    f"Hint: Check if the health check command is working correctly, "
                    f"the application is starting properly, and the health check interval is appropriate."
                )

            wrapped.reload()  # Refresh container state
            health = wrapped.attrs.get("State", {}).get("Health", {})

            # No health check configured
            if not health:
                raise RuntimeError(
                    "No health check configured for container. "
                    "Add HEALTHCHECK instruction to Dockerfile or configure health check in container creation. "
                    "Example: HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1"
                )

            status = health.get("Status")

            if status == "healthy":
                return
            elif status == "unhealthy":
                # Get the last health check log for better error reporting
                log = health.get("Log", [])
                last_log = log[-1] if log else {}
                exit_code = last_log.get("ExitCode", "unknown")
                output = last_log.get("Output", "no output")

                raise RuntimeError(
                    f"Container health check reported unhealthy. "
                    f"Exit code: {exit_code}, "
                    f"Output: {output}. "
                    f"Hint: Check the health check command, ensure the application is responding correctly, "
                    f"and verify the health check endpoint or command is working as expected."
                )

            time.sleep(self._poll_interval)


class PortWaitStrategy(WaitStrategy):
    """
    Wait for a port to be available on the container.

    This strategy attempts to establish a TCP connection to a specified port
    on the container and waits until the connection succeeds. It's useful for
    waiting for services that need to be listening on a specific port.

    Args:
        port: The port number to check for availability

    Example:
        # Wait for port 8080 to be available
        strategy = PortWaitStrategy(8080)

        # Wait for database port with custom timeout
        strategy = PortWaitStrategy(5432).with_startup_timeout(30)
    """

    def __init__(self, port: int) -> None:
        super().__init__()
        self._port = port

    def wait_until_ready(self, container: WaitStrategyTarget) -> None:
        """
        Wait until the specified port is available for connection.

        Args:
            container: The container to monitor

        Raises:
            TimeoutError: If the port doesn't become available within the timeout period
        """
        start_time = time.time()
        host = container.get_container_host_ip()
        port = int(container.get_exposed_port(self._port))

        while True:
            if time.time() - start_time > self._startup_timeout:
                raise TimeoutError(
                    f"Port {self._port} not available within {self._startup_timeout} seconds. "
                    f"Attempted connection to {host}:{port}. "
                    f"Hint: Check if the service is configured to listen on port {self._port}, "
                    f"the service is starting correctly, and there are no firewall or network issues."
                )

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect((host, port))
                    return
            except (socket.timeout, ConnectionRefusedError, OSError):
                time.sleep(self._poll_interval)


class FileExistsWaitStrategy(WaitStrategy):
    """
    Wait for a file to exist on the host filesystem.

    This strategy waits for a specific file to exist on the host filesystem,
    typically used for waiting for files created by containers via volume mounts.
    This is useful for scenarios like Docker-in-Docker where certificate files
    need to be generated before they can be used.

    Args:
        file_path: Path to the file to wait for (can be str or Path object)

    Example:
        # Wait for a certificate file
        strategy = FileExistsWaitStrategy("/tmp/certs/ca.pem")

        # Wait for a configuration file
        from pathlib import Path
        strategy = FileExistsWaitStrategy(Path("/tmp/config/app.conf"))
    """

    def __init__(self, file_path: Union[str, Path]) -> None:
        super().__init__()
        self._file_path = Path(file_path)

    def wait_until_ready(self, container: WaitStrategyTarget) -> None:
        """
        Wait until the specified file exists on the host filesystem.

        Args:
            container: The container (used for timeout/polling configuration)

        Raises:
            TimeoutError: If the file doesn't exist within the timeout period
        """
        start_time = time.time()

        logger.debug(
            f"FileExistsWaitStrategy: Waiting for file {self._file_path} with timeout {self._startup_timeout}s"
        )

        while True:
            if time.time() - start_time > self._startup_timeout:
                # Check what files actually exist in the directory
                parent_dir = self._file_path.parent
                existing_files = []
                if parent_dir.exists():
                    existing_files = [str(f) for f in parent_dir.rglob("*") if f.is_file()]

                logger.error(f"FileExistsWaitStrategy: File {self._file_path} not found after timeout")
                logger.debug(f"FileExistsWaitStrategy: Parent directory exists: {parent_dir.exists()}")
                logger.debug(f"FileExistsWaitStrategy: Files in parent directory: {existing_files}")

                raise TimeoutError(
                    f"File {self._file_path} did not exist within {self._startup_timeout:.3f} seconds. "
                    f"Parent directory exists: {parent_dir.exists()}. "
                    f"Files in parent directory: {existing_files}. "
                    f"Hint: Check if the container is configured to create the file at the expected location, "
                    f"and verify that volume mounts are set up correctly."
                )

            if self._file_path.is_file():
                logger.debug(
                    f"FileExistsWaitStrategy: File {self._file_path} found after {time.time() - start_time:.2f}s"
                )
                return

            logger.debug(
                f"FileExistsWaitStrategy: Polling - file {self._file_path} not found yet, elapsed: {time.time() - start_time:.2f}s"
            )
            time.sleep(self._poll_interval)


class ContainerStatusWaitStrategy(WaitStrategy):
    """
    The possible values for the container status are:
        created
        running
        paused
        restarting
        exited
        removing
        dead
    https://docs.docker.com/reference/cli/docker/container/ls/#status
    """

    CONTINUE_STATUSES = frozenset(("created", "restarting"))

    def __init__(self) -> None:
        super().__init__()

    def wait_until_ready(self, container: WaitStrategyTarget) -> None:
        result = self._poll(lambda: self.running(self.get_status(container)))
        if not result:
            raise TimeoutError("container did not become running")

    @staticmethod
    def running(status: str) -> bool:
        if status == "running":
            logger.debug("status is now running")
            return True
        if status in ContainerStatusWaitStrategy.CONTINUE_STATUSES:
            logger.debug(
                "status is %s, which is valid for continuing (%s)",
                status,
                ContainerStatusWaitStrategy.CONTINUE_STATUSES,
            )
            return False
        raise StopIteration(f"container status not valid for continuing: {status}")

    def get_status(self, container: Any) -> str:
        from testcontainers.core.container import DockerContainer

        if isinstance(container, DockerContainer):
            return self._get_status_tc_container(container)
        if isinstance(container, DockerCompose):
            return self._get_status_compose_container(container)
        raise TypeError(f"not supported operation: 'get_status' for type: {type(container)}")

    @staticmethod
    def _get_status_tc_container(container: "DockerContainer") -> str:
        logger.debug("fetching status of container %s", container)
        wrapped = container.get_wrapped_container()
        wrapped.reload()
        return cast("str", wrapped.status)

    @staticmethod
    def _get_status_compose_container(container: DockerCompose) -> str:
        logger.debug("fetching status of compose container %s", container)
        raise NotImplementedError


class CompositeWaitStrategy(WaitStrategy):
    """
    Wait for multiple conditions to be satisfied in sequence.

    This strategy allows combining multiple wait strategies that must all be satisfied.
    Each strategy is executed in the order they were added, and all must succeed
    for the composite strategy to be considered ready.

    Args:
        strategies: Variable number of WaitStrategy objects to execute in sequence

    Example:
        # Wait for log message AND file to exist
        strategy = CompositeWaitStrategy(
            LogMessageWaitStrategy("API listen on"),
            FileExistsWaitStrategy("/tmp/certs/ca.pem")
        )

        # Wait for multiple conditions
        strategy = CompositeWaitStrategy(
            LogMessageWaitStrategy("Database ready"),
            PortWaitStrategy(5432),
            HttpWaitStrategy(8080, "/health").for_status_code(200)
        )
    """

    def __init__(self, *strategies: WaitStrategy) -> None:
        super().__init__()
        self._strategies = list(strategies)

    def with_poll_interval(self, interval: Union[float, timedelta]) -> Self:
        super().with_poll_interval(interval)
        for _strategy in self._strategies:
            _strategy.with_poll_interval(interval)
        return self

    def with_startup_timeout(self, timeout: Union[int, timedelta]) -> Self:
        super().with_startup_timeout(timeout)
        for _strategy in self._strategies:
            _strategy.with_startup_timeout(timeout)
        return self

    def with_transient_exceptions(self, *transient_exceptions: type[Exception]) -> Self:
        super().with_transient_exceptions(*transient_exceptions)
        for _strategy in self._strategies:
            _strategy.with_transient_exceptions(*transient_exceptions)
        return self

    def wait_until_ready(self, container: WaitStrategyTarget) -> None:
        """
        Wait until all contained strategies are ready.

        Args:
            container: The container to monitor

        Raises:
            TimeoutError: If any strategy doesn't become ready within the timeout period
        """
        logger.debug(f"CompositeWaitStrategy: Starting execution of {len(self._strategies)} strategies")

        for i, strategy in enumerate(self._strategies):
            try:
                logger.debug(
                    f"CompositeWaitStrategy: Executing strategy {i + 1}/{len(self._strategies)}: {type(strategy).__name__}"
                )
                strategy.wait_until_ready(container)
                logger.debug(f"CompositeWaitStrategy: Strategy {i + 1}/{len(self._strategies)} completed successfully")
            except TimeoutError as e:
                logger.error(f"CompositeWaitStrategy: Strategy {i + 1}/{len(self._strategies)} failed: {e}")
                raise TimeoutError(
                    f"Composite wait strategy failed at step {i + 1}/{len(self._strategies)}: {e}"
                ) from e

        logger.debug("CompositeWaitStrategy: All strategies completed successfully")


__all__ = [
    "CompositeWaitStrategy",
    "ContainerStatusWaitStrategy",
    "FileExistsWaitStrategy",
    "HealthcheckWaitStrategy",
    "HttpWaitStrategy",
    "LogMessageWaitStrategy",
    "PortWaitStrategy",
    "WaitStrategy",
    "WaitStrategyTarget",
]
