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
from time import sleep

import wrapt
from testcontainers.core.progress_bar import ConsoleProgressBar

from testcontainers.core import config
from testcontainers.core.exceptions import TimeoutException


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
        bar = ConsoleProgressBar().bar
        logging.warning("Waiting for container to start")
        for _ in bar(range(0, config.max_tries)):
            try:
                return wrapped(*args, **kwargs)
            except Exception as e:
                sleep(config.sleep_time)
                exception = e
        raise TimeoutException(
            """Wait time exceeded {0} sec.
                Method {1}, args {2} , kwargs {3}.
                 Exception {4}""".format(config.max_tries,
                                         wrapped.__name__,
                                         args, kwargs, exception))

    return wrapper
