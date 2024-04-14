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
from typing import TYPE_CHECKING, Any, Callable, Union

import wrapt

from testcontainers.core.config import testcontainers_config as config
from testcontainers.core.utils import setup_logger

if TYPE_CHECKING:
    from testcontainers.core.container import DockerContainer

logger = setup_logger(__name__)

# Get a tuple of transient exceptions for which we'll retry. Other exceptions will be raised.
TRANSIENT_EXCEPTIONS = (TimeoutError, ConnectionError)


def wait_container_is_ready(*transient_exceptions) -> Callable:
    """
    Wait until container is ready.

    Function that spawn container should be decorated by this method Max wait is configured by
    config. Default is 120 sec. Polling interval is 1 sec.

    Args:
        *transient_exceptions: Additional transient exceptions that should be retried if raised. Any
            non-transient exceptions are fatal, and the exception is re-raised immediately.
    """
    transient_exceptions = TRANSIENT_EXCEPTIONS + tuple(transient_exceptions)

    @wrapt.decorator
    def wrapper(wrapped: Callable, instance: Any, args: list, kwargs: dict) -> Any:
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

    return wrapper


@wait_container_is_ready()
def wait_for(condition: Callable[..., bool]) -> bool:
    return condition()


def wait_for_logs(
    container: "DockerContainer", predicate: Union[Callable, str], timeout: float = config.timeout, interval: float = 1
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

    Returns:
        duration: Number of seconds until the predicate was satisfied.
    """
    if isinstance(predicate, str):
        predicate = re.compile(predicate, re.MULTILINE).search
    start = time.time()
    while True:
        duration = time.time() - start
        stdout = container.get_logs()[0].decode()
        stderr = container.get_logs()[1].decode()
        if predicate(stdout) or predicate(stderr):
            return duration
        if duration > timeout:
            raise TimeoutError(f"Container did not emit logs satisfying predicate in {timeout:.3f} " "seconds")
        time.sleep(interval)
