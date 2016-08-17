import logging
from time import sleep

import wrapt

from testcontainers import config
from testcontainers.brogress_bar import ConsoleProgressBar
from testcontainers.exceptions import TimeoutException


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
        raise TimeoutException("Wait time exceeded {} sec. {}".format(config.max_tries, exception))

    return wrapper
