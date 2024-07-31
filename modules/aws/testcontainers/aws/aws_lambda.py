import os
from typing import Union

import httpx

from testcontainers.core.image import DockerImage
from testcontainers.generic.server import ServerContainer

RIE_PATH = "/2015-03-31/functions/function/invocations"
# AWS OS-only base images contain an Amazon Linux distribution and the runtime interface emulator (RIE) for Lambda.


class AWSLambdaContainer(ServerContainer):
    """
    AWS Lambda container that is based on a custom image.

    Example:

        .. doctest::

            >>> from testcontainers.aws import AWSLambdaContainer
            >>> from testcontainers.core.waiting_utils import wait_for_logs
            >>> from testcontainers.core.image import DockerImage

            >>> with DockerImage(path="./modules/aws/tests/lambda_sample", tag="test-lambda:latest") as image:
            ...     with AWSLambdaContainer(image=image, port=8080) as func:
            ...         response = func.send_request(data={'payload': 'some data'})
            ...         assert response.status_code == 200
            ...         assert "Hello from AWS Lambda using Python" in response.json()
            ...         delay = wait_for_logs(func, "START RequestId:")

    :param image: Docker image to be used for the container.
    :param port: Port to be exposed on the container (default: 8080).
    """

    def __init__(self, image: Union[str, DockerImage], port: int = 8080) -> None:
        super().__init__(port, str(image))
        self.with_env("AWS_DEFAULT_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-west-1"))
        self.with_env("AWS_ACCESS_KEY_ID", os.environ.get("AWS_ACCESS_KEY_ID", "testcontainers-aws"))
        self.with_env("AWS_SECRET_ACCESS_KEY", os.environ.get("AWS_SECRET_ACCESS_KEY", "testcontainers-aws"))

    def get_api_url(self) -> str:
        return self._create_connection_url() + RIE_PATH

    def send_request(self, data: dict) -> httpx.Response:
        """
        Send a request to the AWS Lambda function.

        :param data: Data to be sent to the AWS Lambda function.
        :return: Response from the AWS Lambda function.
        """
        client = self.get_client()
        return client.post(self.get_api_url(), json=data)
