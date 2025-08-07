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
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Union

from testcontainers.core.utils import setup_logger

# Import base classes from waiting_utils to make them available for tests
from .waiting_utils import WaitStrategy

if TYPE_CHECKING:
    from .waiting_utils import WaitStrategyTarget

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

    def with_startup_timeout(self, timeout: Union[int, timedelta]) -> "LogMessageWaitStrategy":
        """Set the maximum time to wait for the container to be ready."""
        if isinstance(timeout, timedelta):
            self._startup_timeout = int(timeout.total_seconds())
        else:
            self._startup_timeout = timeout
        return self

    def with_poll_interval(self, interval: Union[float, timedelta]) -> "LogMessageWaitStrategy":
        """Set how frequently to check if the container is ready."""
        if isinstance(interval, timedelta):
            self._poll_interval = interval.total_seconds()
        else:
            self._poll_interval = interval
        return self

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
