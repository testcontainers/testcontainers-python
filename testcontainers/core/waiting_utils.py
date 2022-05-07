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

import wrapt

from testcontainers.core import config
from testcontainers.core.exceptions import TimeoutException
from testcontainers.core.utils import setup_logger

logger = setup_logger(__name__)


# Get a tuple of transient exceptions for which we'll retry. Other exceptions will be raised.
TRANSIENT_EXCEPTIONS = (TimeoutError, ConnectionError)


def wait_container_is_ready(*transient_exceptions):
    """
    Wait until container is ready.
    Function that spawn container should be decorated by this method
    Max wait is configured by config. Default is 120 sec.
    Polling interval is 1 sec.
    :return:
    """

    transient_exceptions = TRANSIENT_EXCEPTIONS + tuple(transient_exceptions)

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        exception = None
        logger.info("Waiting to be ready...")
        for attempt_no in range(config.MAX_TRIES):
            try:
                return wrapped(*args, **kwargs)
            except transient_exceptions as e:
                logger.debug(f"Connection attempt '{attempt_no + 1}' of '{config.MAX_TRIES + 1}' "
                             f"failed: {traceback.format_exc()}")
                time.sleep(config.SLEEP_TIME)
                exception = e
        raise TimeoutException(
            f'Wait time ({config.MAX_TRIES * config.SLEEP_TIME}s) exceeded for {wrapped.__name__}'
            f'(args: {args}, kwargs {kwargs}). Exception: {exception}'
        )

    return wrapper


@wait_container_is_ready()
def wait_for(condition):
    return condition()


def wait_for_logs(container, predicate, timeout=None, interval=1):
    """
    Wait for the container to emit logs satisfying the predicate.

    Parameters
    ----------
    container : DockerContainer
        Container whose logs to wait for.
    predicate : callable or str
        Predicate that should be satisfied by the logs. If a string, the it is used as the pattern
        for a multiline regular expression search.
    timeout : float or None
        Number of seconds to wait for the predicate to be satisfied. Defaults to wait indefinitely.
    interval : float
        Interval at which to poll the logs.

    Returns
    -------
    duration : float
        Number of seconds until the predicate was satisfied.
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
        if timeout and duration > timeout:
            raise TimeoutError("container did not emit logs satisfying predicate in %.3f seconds"
                               % timeout)
        time.sleep(interval)
