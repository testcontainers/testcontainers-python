"""
Docker compose support
======================

Allows to spin up services configured via :code:`docker-compose.yml`.
"""

import requests
import subprocess

from testcontainers.core.waiting_utils import wait_container_is_ready
from testcontainers.core.exceptions import NoSuchPortExposed


class DockerCompose(object):
    """
    Docker compose containers.

    Example
    -------
    ::

        with DockerCompose("/home/project",
                           compose_file_name=["docker-compose-1.yml", "docker-compose-2.yml"],
                           pull=True) as compose:
            host = compose.get_service_host("hub", 4444)
            port = compose.get_service_port("hub", 4444)
            driver = webdriver.Remote(
                command_executor=("http://{}:{}/wd/hub".format(host,port)),
                desired_capabilities=CHROME,
            )
            driver.get("http://automation-remarks.com")
            stdout, stderr = compose.get_logs()
            if stderr:
                print("Errors\\n:{}".format(stderr))


    .. code-block:: yaml

        hub:
        image: selenium/hub
        ports:
        - "4444:4444"
        firefox:
        image: selenium/node-firefox
        links:
            - hub
        expose:
            - "5555"
        chrome:
        image: selenium/node-chrome
        links:
            - hub
        expose:
            - "5555"
    """

    def __init__(
            self,
            filepath,
            compose_file_name="docker-compose.yml",
            pull=False,
            env_file=None):
        self.filepath = filepath
        self.compose_file_names = compose_file_name if isinstance(
            compose_file_name, (list, tuple)
        ) else [compose_file_name]
        self.pull = pull
        self.env_file = env_file

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def docker_compose_command(self):
        docker_compose_cmd = ['docker-compose']
        for file in self.compose_file_names:
            docker_compose_cmd += ['-f', file]
        if self.env_file:
            docker_compose_cmd += ['--env-file', self.env_file]
        return docker_compose_cmd

    def start(self):
        if self.pull:
            pull_cmd = self.docker_compose_command() + ['pull']
            subprocess.call(pull_cmd, cwd=self.filepath)

        up_cmd = self.docker_compose_command() + ['up', '-d']
        subprocess.call(up_cmd, cwd=self.filepath)

    def stop(self):
        down_cmd = self.docker_compose_command() + ['down', '-v']
        subprocess.call(down_cmd, cwd=self.filepath)

    def get_logs(self):
        logs_cmd = self.docker_compose_command() + ["logs"]
        result = subprocess.run(
            logs_cmd,
            cwd=self.filepath,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout, result.stderr

    def get_service_port(self, service_name, port):
        return self._get_service_info(service_name, port)[1]

    def get_service_host(self, service_name, port):
        return self._get_service_info(service_name, port)[0]

    def _get_service_info(self, service, port):
        port_cmd = self.docker_compose_command() + ["port", service, str(port)]
        output = subprocess.check_output(port_cmd, cwd=self.filepath).decode("utf-8")
        result = str(output).rstrip().split(":")
        if len(result) == 1:
            raise NoSuchPortExposed("Port {} was not exposed for service {}"
                                    .format(port, service))
        return result

    @wait_container_is_ready()
    def wait_for(self, url):
        requests.get(url)
        return self
