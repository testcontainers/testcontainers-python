import os
from typing import Optional

import httpx

from testcontainers.core.generic import SrvContainer

RIE_PATH = "/2015-03-31/functions/function/invocations"
# AWS OS-only base images contain an Amazon Linux distribution and the runtime interface emulator.


class AWSLambdaContainer(SrvContainer):
    """
    AWS Lambda container that is based on a custom image.

    Example:

        .. doctest::

            >>> from testcontainers.aws import AWSLambdaContainer
            >>> from testcontainers.core.waiting_utils import wait_for_logs

            >>> with AWSLambdaContainer(path="./modules/aws/tests/lambda_sample", port=8080, tag="lambda_func:latest") as func:
            ...     response = func.send_request(data={'payload': 'some data'})
            ...     assert response.status_code == 200
            ...     assert "Hello from AWS Lambda using Python" in response.json()
            ...     delay = wait_for_logs(func, "START RequestId:")
    """

    def __init__(
        self,
        path: str,
        port: int = 8080,
        region_name: Optional[str] = None,
        tag: Optional[str] = None,
        image_cleanup: bool = True,
    ) -> None:
        """
        :param path: Path to the AWS Lambda dockerfile.
        :param port: Port to be exposed on the container (default: 8080).
        :param region_name: AWS region name (default: None).
        :param tag: Tag for the image to be built (default: None).
        :param image_cleanup: Clean up the image after the container is stopped (default: True).
        """
        super().__init__(path, port, tag, image_cleanup)
        self.region_name = region_name or os.environ.get("AWS_DEFAULT_REGION", "us-west-1")
        self.with_env("AWS_DEFAULT_REGION", self.region_name)
        self.with_env("AWS_ACCESS_KEY_ID", "testcontainers-aws")
        self.with_env("AWS_SECRET_ACCESS_KEY", "testcontainers-aws")

    def get_api_url(self) -> str:
        return self._create_connection_url() + RIE_PATH

    def send_request(self, data: dict) -> httpx.Response:
        """
        Send a request to the AWS Lambda function.

        :param data: Data to be sent to the AWS Lambda function.
        :return: Response from the AWS Lambda function.
        """
        client = httpx.Client()
        return client.post(self.get_api_url(), json=data)

    def get_stdout(self) -> str:
        return self.get_logs()[0].decode("utf-8")
