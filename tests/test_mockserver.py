from http import HTTPStatus

import requests
from mockserver import request as request_expectation, response as response_expectation

from testcontainers.mockserver import MockServerContainer


def test_mockserver() -> None:
    with MockServerContainer() as mockserver:
        mockserver_client = mockserver.get_client()
        mockserver_client.stub(request_expectation(method='GET', path='/path'),
                               response=response_expectation(code=HTTPStatus.OK))

        response = requests.get(f'{mockserver.base_url}/path')
        assert response.status_code == HTTPStatus.OK

        mockserver_client.verify()
