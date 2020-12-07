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

import wrapt

from testcontainers.core import config
from testcontainers.core.exceptions import TimeoutException
from testcontainers.core.utils import setup_logger

logger = setup_logger(__name__)


def wait_container_is_ready():
    """
    Wait until container is ready.
    Function that spawn container should be decorated by this method
    Max wait is configured by config. Default is 120 sec.
    Polling interval is 1 sec.
    :return:
    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        exception = None
        logger.info("Waiting to be ready...")
        for _ in range(0, config.MAX_TRIES):
            try:
                return wrapped(*args, **kwargs)
            except Exception as e:
                time.sleep(config.SLEEP_TIME)
                exception = e
        raise TimeoutException(
            """Wait time exceeded {0} sec.
                Method {1}, args {2} , kwargs {3}.
                    Exception {4}""".format(config.MAX_TRIES,
                                            wrapped.__name__,
                                            args, kwargs, exception))

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
        if predicate(container._container.logs().decode()):
            return duration
        if timeout and duration > timeout:
            raise TimeoutError("container did not emit logs satisfying predicate in %.3f seconds"
                               % timeout)
        time.sleep(interval)
