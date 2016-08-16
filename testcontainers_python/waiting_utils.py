import logging
from time import sleep

import wrapt

from testcontainers_python import config
from testcontainers_python.brogress_bar import ConsoleProgressBar
from testcontainers_python.exceptions import TimeoutException


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
        bar = ConsoleProgressBar().bar
        logging.warning("Waiting for container to start")
        for _ in bar(range(0, config.max_tries)):
            try:
                return wrapped(*args, **kwargs)
            except Exception:
                sleep(config.sleep_time)
        raise TimeoutException("Wait time exceeded {} sec.".format(config.max_tries))

    return wrapper
