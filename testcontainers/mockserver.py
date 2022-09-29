from typing import Any

import requests
from mockserver import MockServerClient

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class MockServerContainer(DockerContainer):
    """
    MockServer container.

    Example
    -------
    ::

        with MockServerContainer() as mockserver:
            mockserver_client = mockserver.get_client()
            mockserver_client.stub(request(method='GET', path='/path'),
                                   response=response(code=HTTPStatus.OK))

            response = requests.get(f'{mockserver.base_url}/path')
            assert response.status_code == HTTPStatus.OK

            mockserver_client.verify()
    """

    EDGE_PORT = 1080
    IMAGE = 'mockserver/mockserver:latest'

    def __init__(self, image: str = IMAGE, **kwargs: Any):
        super().__init__(image, **kwargs)
        self.with_exposed_ports(MockServerContainer.EDGE_PORT)

    @property
    def base_url(self) -> str:
        return f'http://{self.get_container_host_ip()}:{self.get_exposed_port(self.EDGE_PORT)}'

    def get_client(self) -> MockServerClient:
        return MockServerClient(f'{self.base_url}/mockserver')

    @wait_container_is_ready(requests.ConnectionError)
    def _connect(self):
        requests.get(self.base_url)

    def start(self):
        super().start()
        self._connect()
        return self
