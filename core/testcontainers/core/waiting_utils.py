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


import re
import time
import warnings
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Callable, Optional, Protocol, TypeVar, Union, cast

import wrapt
from typing_extensions import Self

from testcontainers.core.config import testcontainers_config
from testcontainers.core.utils import setup_logger

logger = setup_logger(__name__)

# Get a tuple of transient exceptions for which we'll retry. Other exceptions will be raised.
TRANSIENT_EXCEPTIONS = (TimeoutError, ConnectionError)

# Type variables for generic functions
F = TypeVar("F", bound=Callable[..., Any])


class WaitStrategyTarget(Protocol):
    """
    Protocol defining the interface that containers must implement for wait strategies.
    This allows wait strategies to work with both DockerContainer and ComposeContainer
    without requiring inheritance or type ignores.
    Implementation requirement:
    - DockerContainer: Implements this protocol (see core/tests/test_protocol_compliance.py)
    - ComposeContainer: Implements this protocol (see core/tests/test_protocol_compliance.py)
    """

    def get_container_host_ip(self) -> str:
        """Get the host IP address for the container."""
        ...

    def get_exposed_port(self, port: int) -> int:
        """Get the exposed port mapping for the given internal port."""
        ...

    def get_wrapped_container(self) -> Any:
        """Get the underlying container object."""
        ...

    def get_logs(self) -> tuple[bytes, bytes]:
        """Get container logs as (stdout, stderr) tuple."""
        ...

    def reload(self) -> None:
        """Reload container information."""
        ...

    @property
    def status(self) -> str:
        """Get container status."""
        ...


class WaitStrategy(ABC):
    """Base class for all wait strategies."""

    def __init__(self) -> None:
        self._startup_timeout: float = testcontainers_config.timeout
        self._poll_interval: float = testcontainers_config.sleep_time
        self._transient_exceptions: list[type[Exception]] = [*TRANSIENT_EXCEPTIONS]

    def with_startup_timeout(self, timeout: Union[int, timedelta]) -> Self:
        """Set the maximum time to wait for the container to be ready."""
        if isinstance(timeout, timedelta):
            self._startup_timeout = float(int(timeout.total_seconds()))
        else:
            self._startup_timeout = float(timeout)
        return self

    def with_poll_interval(self, interval: Union[float, timedelta]) -> Self:
        """Set how frequently to check if the container is ready."""
        if isinstance(interval, timedelta):
            self._poll_interval = interval.total_seconds()
        else:
            self._poll_interval = interval
        return self

    def with_transient_exceptions(self, *transient_exceptions: type[Exception]) -> Self:
        self._transient_exceptions.extend(transient_exceptions)
        return self

    @abstractmethod
    def wait_until_ready(self, container: WaitStrategyTarget) -> None:
        """Wait until the container is ready."""
        pass

    def _poll(self, check: Callable[[], bool], transient_exceptions: Optional[list[type[Exception]]] = None) -> bool:
        if not transient_exceptions:
            all_te_types = self._transient_exceptions
        else:
            all_te_types = [*self._transient_exceptions, *(transient_exceptions or [])]

        start = time.time()
        while True:
            start_attempt = time.time()
            duration = start_attempt - start
            if duration > self._startup_timeout:
                return False

            # noinspection PyBroadException
            try:
                result = check()
                if result:
                    return result
            except StopIteration:
                return False
            except Exception as e:  # noqa: E722, RUF100
                is_transient = False
                for et in all_te_types:
                    if isinstance(e, et):
                        is_transient = True
                if not is_transient:
                    raise RuntimeError(f"exception while checking for strategy {self}") from e

            seconds_left_until_next = self._poll_interval - (time.time() - start_attempt)
            time.sleep(max(0.0, seconds_left_until_next))


# Keep existing wait_container_is_ready but make it use the new system internally
def wait_container_is_ready(*transient_exceptions: type[Exception]) -> Callable[[F], F]:
    """
    Legacy wait decorator that uses the new wait strategy system internally.
    Maintains backwards compatibility with existing code.
    This decorator can be used to wait for a function to succeed without raising
    transient exceptions. It's useful for simple wait scenarios, but for more
    complex cases, consider using structured wait strategies directly.
    Example:
        @wait_container_is_ready(HTTPError, URLError)
        def check_http(container):
            with urlopen("http://localhost:8080") as response:
                return response.status == 200
        # For more complex scenarios, use structured wait strategies:
        container.waiting_for(HttpWaitStrategy(8080).for_status_code(200))
    """
    warnings.warn(
        "The @wait_container_is_ready decorator is deprecated and will be removed in a future version. "
        "Use structured wait strategies instead: "
        "container.waiting_for(HttpWaitStrategy(8080).for_status_code(200)) or "
        "container.waiting_for(LogMessageWaitStrategy('ready'))",
        DeprecationWarning,
        stacklevel=2,
    )

    class LegacyWaitStrategy(WaitStrategy):
        def __init__(self, func: Callable[..., Any], instance: Any, args: list[Any], kwargs: dict[str, Any]):
            super().__init__()
            self.func = func
            self.instance = instance
            self.args = args
            self.kwargs = kwargs
            self.transient_exceptions: tuple[type[Exception], ...] = TRANSIENT_EXCEPTIONS + tuple(transient_exceptions)

        def wait_until_ready(self, container: WaitStrategyTarget) -> Any:
            start_time = time.time()
            while True:
                try:
                    # Handle different function call patterns:
                    # 1. Standalone functions (like wait_for): call with just args/kwargs
                    # 2. Methods: call with instance as first argument
                    if self.instance is None:
                        # Standalone function case
                        result = self.func(*self.args, **self.kwargs)
                    elif self.instance is container:
                        # Staticmethod case: self.instance is the container
                        result = self.func(*self.args, **self.kwargs)
                    else:
                        # Method case: self.instance is the instance (self)
                        result = self.func(self.instance, *self.args, **self.kwargs)
                    return result
                except self.transient_exceptions as e:
                    if time.time() - start_time > self._startup_timeout:
                        raise TimeoutError(
                            f"Wait time ({self._startup_timeout}s) exceeded for {self.func.__name__}"
                            f"(args: {self.args}, kwargs: {self.kwargs}). Exception: {e}. "
                            f"Hint: Check if the container is ready, the function parameters are correct, "
                            f"and the expected conditions are met for the function to succeed."
                        ) from e
                    logger.debug(f"Connection attempt failed: {e!s}")
                    time.sleep(self._poll_interval)

    @wrapt.decorator  # type: ignore[misc]
    def wrapper(wrapped: Callable[..., Any], instance: Any, args: list[Any], kwargs: dict[str, Any]) -> Any:
        # Use the LegacyWaitStrategy to handle retries with proper timeout
        strategy = LegacyWaitStrategy(wrapped, instance, args, kwargs)
        # For backwards compatibility, assume the instance is the container
        container = instance if hasattr(instance, "get_container_host_ip") else args[0] if args else None
        if container:
            return strategy.wait_until_ready(container)
        else:
            # Fallback to direct call if we can't identify the container
            return wrapped(*args, **kwargs)

    return cast("Callable[[F], F]", wrapper)


@wait_container_is_ready()
def wait_for(condition: Callable[..., bool]) -> bool:
    warnings.warn(
        "The wait_for function is deprecated and will be removed in a future version. "
        "Use structured wait strategies instead: "
        "container.waiting_for(LogMessageWaitStrategy('ready')) or "
        "container.waiting_for(HttpWaitStrategy(8080).for_status_code(200))",
        DeprecationWarning,
        stacklevel=2,
    )
    return condition()


_NOT_EXITED_STATUSES = {"running", "created"}


def wait_for_logs(
    container: WaitStrategyTarget,
    predicate: Union[Callable[[str], bool], str, WaitStrategy],
    timeout: float = testcontainers_config.timeout,
    interval: float = 1,
    predicate_streams_and: bool = False,
    raise_on_exit: bool = False,
    #
) -> float:
    """
    Enhanced version of wait_for_logs that supports both old and new interfaces.

    This function waits for container logs to satisfy a predicate. It supports
    multiple input types for the predicate and maintains backwards compatibility
    with existing code while adding support for the new WaitStrategy system.

    This is a convenience function that can be used for simple log-based waits.
    For more complex scenarios, consider using structured wait strategies directly.

    Args:
        container: The DockerContainer to monitor
        predicate: The predicate to check against logs. Can be:
            - A callable function that takes log text and returns bool
            - A string that will be compiled to a regex pattern
            - A WaitStrategy object
        timeout: Maximum time to wait in seconds (default: config.timeout)
        interval: How frequently to check in seconds (default: 1)
        predicate_streams_and: If True, predicate must match both stdout and stderr (default: False)
        raise_on_exit: If True, raise RuntimeError if container exits before predicate matches (default: False)

    Returns:
        The time in seconds that was spent waiting

    Raises:
        TimeoutError: If the predicate is not satisfied within the timeout period
        RuntimeError: If raise_on_exit is True and container exits before predicate matches

    Example:
        # Wait for a simple string
        wait_for_logs(container, "ready for start")

        # Wait with custom predicate
        wait_for_logs(container, lambda logs: "database" in logs and "ready" in logs)

        # Wait with WaitStrategy
        strategy = LogMessageWaitStrategy("ready")
        wait_for_logs(container, strategy)

        # For more complex scenarios, use structured wait strategies directly:
        container.waiting_for(LogMessageWaitStrategy("ready"))
    """
    if isinstance(predicate, WaitStrategy):
        start = time.time()
        predicate.with_startup_timeout(int(timeout)).with_poll_interval(interval)
        predicate.wait_until_ready(container)
        return time.time() - start
    else:
        # Only warn for legacy usage (string or callable predicates, not WaitStrategy objects)
        warnings.warn(
            "The wait_for_logs function with string or callable predicates is deprecated and will be removed in a future version. "
            "Use structured wait strategies instead: "
            "container.waiting_for(LogMessageWaitStrategy('ready')) or "
            "container.waiting_for(LogMessageWaitStrategy(re.compile(r'pattern')))",
            DeprecationWarning,
            stacklevel=2,
        )

    # Original implementation for backwards compatibility
    re_predicate: Optional[Callable[[str], Any]] = None
    if timeout is None:
        timeout = testcontainers_config.timeout
    if isinstance(predicate, str):
        re_predicate = re.compile(predicate, re.MULTILINE).search
    elif callable(predicate):
        # some modules like mysql sends the search directly to the predicate
        re_predicate = predicate
    else:
        raise TypeError("Predicate must be a string or callable")
    wrapped = container.get_wrapped_container()
    start = time.time()
    while True:
        duration = time.time() - start
        stdout_b, stderr_b = container.get_logs()
        stdout = stdout_b.decode()
        stderr = stderr_b.decode()
        predicate_result = (
            re_predicate(stdout) or re_predicate(stderr)
            if predicate_streams_and is False
            else re_predicate(stdout) and re_predicate(stderr)
            #
        )
        if predicate_result:
            return duration
        if duration > timeout:
            # Get current logs and status for debugging
            stdout_str, stderr_str = _get_container_logs_for_debugging(container)
            status_info = _get_container_status_info(container)

            raise TimeoutError(
                f"Container did not emit logs satisfying predicate in {timeout:.3f} seconds. "
                f"Container status: {status_info['status']}, health: {status_info['health_status']}. "
                f"Recent stdout: {stdout_str}. "
                f"Recent stderr: {stderr_str}. "
                f"Hint: Check if the container is starting correctly and the expected log pattern is being generated. "
                f"Verify the predicate function or pattern matches the actual log output."
            )
        if raise_on_exit:
            wrapped.reload()
            if wrapped.status not in _NOT_EXITED_STATUSES:
                raise RuntimeError("Container exited before emitting logs satisfying predicate")
        time.sleep(interval)


def _get_container_logs_for_debugging(container: WaitStrategyTarget, max_length: int = 200) -> tuple[str, str]:
    """
    Get container logs for debugging purposes.
    Args:
        container: The container to get logs from
        max_length: Maximum length of log output to include in error messages
    Returns:
        Tuple of (stdout, stderr) as strings
    """
    try:
        stdout_bytes, stderr_bytes = container.get_logs()
        stdout_str = stdout_bytes.decode() if stdout_bytes else ""
        stderr_str = stderr_bytes.decode() if stderr_bytes else ""

        # Truncate if too long
        if len(stdout_str) > max_length:
            stdout_str = "..." + stdout_str[-max_length:]
        if len(stderr_str) > max_length:
            stderr_str = "..." + stderr_str[-max_length:]
        return stdout_str, stderr_str
    except Exception:
        return "(failed to get logs)", "(failed to get logs)"


def _get_container_status_info(container: WaitStrategyTarget) -> dict[str, str]:
    """
    Get container status information for debugging.
    Args:
        container: The container to get status from
    Returns:
        Dictionary with status information
    """
    try:
        wrapped = container.get_wrapped_container()
        wrapped.reload()

        state = wrapped.attrs.get("State", {})
        return {
            "status": wrapped.status,
            "exit_code": str(state.get("ExitCode", "unknown")),
            "error": state.get("Error", ""),
            "health_status": state.get("Health", {}).get("Status", "no health check"),
        }
    except Exception:
        return {
            "status": "unknown",
            "exit_code": "unknown",
            "error": "failed to get status",
            "health_status": "unknown",
        }


__all__ = [
    "WaitStrategy",
    "WaitStrategyTarget",
    "wait_container_is_ready",
    "wait_for",
    "wait_for_logs",
]
