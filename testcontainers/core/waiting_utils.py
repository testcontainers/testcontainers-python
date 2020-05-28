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

import blindspin
import crayons
import requests
import wrapt
from requests import RequestException

from testcontainers.core import config
from testcontainers.core.container import DockerContainer
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
        print(crayons.yellow("Waiting to be ready..."))
        with blindspin.spinner():
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


def wait_for_port(container: DockerContainer, port: int, timeout=None, interval=1):
    """
    Wait for the container port to be available.

    Parameters
    ----------
    container : DockerContainer
        Container whose port to wait for.
    port : int
        Port to check against.
    timeout : float or None
        Number of seconds to wait for the port to be open. Defaults to wait indefinitely.
    interval : float
        Interval at which to poll the port.

    Returns
    -------
    duration : float
        Number of seconds until the check passed.

    """
    start = time.time()
    while True:
        duration = time.time() - start

        # build command
        parts = ["/bin/sh", "-c", "\"true", "&&", "(",
                 "cat", "/proc/net/tcp*", "|", "awk", "'{print $2}'", "|", "grep", "-i", "':0*%x'" % port,
                 "||", "nc", "-vz", "-w", "1", "localhost", "%d" % port,
                 "||", "/bin/bash", "-c", "'</dev/tcp/localhost/%d'" % port, ")\""]

        cmd = ' '.join(parts)

        res = container._container.exec_run(cmd)

        if res.exit_code == 0:
            return duration
        if timeout and duration > timeout:
            raise TimeoutError("container did not start listening on port %d in %.3f seconds"
                               % (port, timeout))
        time.sleep(interval)


def wait_for_http_code(container: DockerContainer, status_code: int, port: int = 80, path: str = '/',
                       scheme: str = 'http', timeout=None, interval=1, request_kwargs: dict = None):
    """
    Wait for a specific http status code.

    Parameters
    ----------
    container : DockerContainer
        Container which is queried for a specific status code.
    status_code : int
        Status code to wait for.
    port : int
        Port to query request on.
    path : str
        Path to use for request. Default is '/'
    scheme : str
        Scheme to use in request query. Default is 'http'
    timeout : float or None
        Number of seconds to wait for the port to be open. Defaults to wait indefinitely.
    interval : float
        Interval at which to poll the port.
    request_kwargs: dict
        kwargs to pass into the request, e.g.: {'verify': False}

    Returns
    -------
    duration : float
        Number of seconds until the check passed.
    """
    if request_kwargs is None:
        request_kwargs = {'timeout': 1.0}
    elif 'timeout' not in request_kwargs:
        request_kwargs['timeout'] = 1.0

    start = time.time()
    # wait for port to open before continuing with http check
    wait_for_port(container, port, timeout, interval)
    while True:
        duration = time.time() - start
        dest = "%s://%s:%d%s" % (scheme,
                                 container.get_container_host_ip(),
                                 int(container.get_exposed_port(port)),
                                 path)
        res = None
        try:
            res = requests.get(dest, **request_kwargs)
        except RequestException:
            pass
        if res and res.status_code == status_code:
            return duration
        if timeout and duration > timeout:
            raise TimeoutError("container did not respond with %d listening on port %d in %.3f seconds"
                               % (status_code, port, timeout))
