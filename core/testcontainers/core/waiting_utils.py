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
import traceback
from typing import TYPE_CHECKING, Any, Callable, Optional, Union, cast

import wrapt

from testcontainers.core.config import testcontainers_config as config
from testcontainers.core.utils import setup_logger

if TYPE_CHECKING:
    from testcontainers.core.container import DockerContainer

logger = setup_logger(__name__)

# Get a tuple of transient exceptions for which we'll retry. Other exceptions will be raised.
TRANSIENT_EXCEPTIONS = (TimeoutError, ConnectionError)


def wait_container_is_ready(*transient_exceptions: type[BaseException]) -> Callable[..., Any]:
    """
    Wait until container is ready.

    Function that spawn container should be decorated by this method Max wait is configured by
    config. Default is 120 sec. Polling interval is 1 sec.

    Args:
        *transient_exceptions: Additional transient exceptions that should be retried if raised. Any
            non-transient exceptions are fatal, and the exception is re-raised immediately.
    """
    transient_exceptions = TRANSIENT_EXCEPTIONS + tuple(transient_exceptions)

    @wrapt.decorator  # type: ignore[misc]
    def wrapper(wrapped: Callable[..., Any], instance: Any, args: list[Any], kwargs: dict[str, Any]) -> Any:
        from testcontainers.core.container import DockerContainer

        if isinstance(instance, DockerContainer):
            logger.info("Waiting for container %s with image %s to be ready ...", instance._container, instance.image)
        else:
            logger.info("Waiting for %s to be ready ...", instance)

        exception = None
        for attempt_no in range(config.max_tries):
            try:
                return wrapped(*args, **kwargs)
            except transient_exceptions as e:
                logger.debug(
                    f"Connection attempt '{attempt_no + 1}' of '{config.max_tries + 1}' "
                    f"failed: {traceback.format_exc()}"
                )
                time.sleep(config.sleep_time)
                exception = e
        raise TimeoutError(
            f"Wait time ({config.timeout}s) exceeded for {wrapped.__name__}(args: {args}, kwargs: "
            f"{kwargs}). Exception: {exception}"
        )

    return cast("Callable[..., Any]", wrapper)


@wait_container_is_ready()
def wait_for(condition: Callable[..., bool]) -> bool:
    return condition()


_NOT_EXITED_STATUSES = {"running", "created"}


def wait_for_logs(
    container: "DockerContainer",
    predicate: Union[Callable[..., bool], str],
    timeout: Union[float, None] = None,
    interval: float = 1,
    predicate_streams_and: bool = False,
    raise_on_exit: bool = False,
    #
) -> float:
    """
    Wait for the container to emit logs satisfying the predicate.

    Args:
        container: Container whose logs to wait for.
        predicate: Predicate that should be satisfied by the logs. If a string, then it is used as
        the pattern for a multiline regular expression search.
        timeout: Number of seconds to wait for the predicate to be satisfied. Defaults to wait
            indefinitely.
        interval: Interval at which to poll the logs.
        predicate_streams_and: should the predicate be applied to both

    Returns:
        duration: Number of seconds until the predicate was satisfied.
    """
    re_predicate: Optional[Callable[[str], Any]] = None
    if timeout is None:
        timeout = config.timeout
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
            raise TimeoutError(f"Container did not emit logs satisfying predicate in {timeout:.3f} seconds")
        if raise_on_exit:
            wrapped.reload()
            if wrapped.status not in _NOT_EXITED_STATUSES:
                raise RuntimeError("Container exited before emitting logs satisfying predicate")
        time.sleep(interval)
