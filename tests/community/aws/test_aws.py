import re
import os

import pytest
from unittest.mock import patch

from testcontainers.core.image import DockerImage
from testcontainers.aws import AWSLambdaContainer
from testcontainers.aws.aws_lambda import RIE_PATH

DOCKER_FILE_PATH = "./modules/aws/tests/lambda_sample"
IMAGE_TAG = "lambda:test"


def test_aws_lambda_container():
    with DockerImage(path=DOCKER_FILE_PATH, tag="test-lambda:latest") as image:
        with AWSLambdaContainer(image=image, port=8080) as func:
            assert func.get_container_host_ip() == "localhost"
            assert func.internal_port == 8080
            assert func.env["AWS_DEFAULT_REGION"] == "us-west-1"
            assert func.env["AWS_ACCESS_KEY_ID"] == "testcontainers-aws"
            assert func.env["AWS_SECRET_ACCESS_KEY"] == "testcontainers-aws"
            assert re.match(rf"http://localhost:\d+{RIE_PATH}", func.get_api_url())
            response = func.send_request(data={"payload": "test"})
            assert response.status_code == 200
            assert "Hello from AWS Lambda using Python" in response.json()
            for log_str in ["START RequestId", "END RequestId", "REPORT RequestId"]:
                assert log_str in func.get_stdout()


def test_aws_lambda_container_external_env_vars():
    vars = {
        "AWS_DEFAULT_REGION": "region",
        "AWS_ACCESS_KEY_ID": "id",
        "AWS_SECRET_ACCESS_KEY": "key",
    }
    with patch.dict(os.environ, vars):
        with DockerImage(path=DOCKER_FILE_PATH, tag="test-lambda-env-vars:latest") as image:
            with AWSLambdaContainer(image=image, port=8080) as func:
                assert func.env["AWS_DEFAULT_REGION"] == "region"
                assert func.env["AWS_ACCESS_KEY_ID"] == "id"
                assert func.env["AWS_SECRET_ACCESS_KEY"] == "key"


def test_aws_lambda_container_no_port():
    with DockerImage(path=DOCKER_FILE_PATH, tag="test-lambda-no-port:latest") as image:
        with AWSLambdaContainer(image=image) as func:
            response = func.send_request(data={"payload": "test"})
            assert response.status_code == 200


def test_aws_lambda_container_no_path():
    with pytest.raises(TypeError):
        with DockerImage(path=DOCKER_FILE_PATH, tag="test-lambda-no-path:latest") as image:
            with AWSLambdaContainer() as func:  # noqa: F841
                pass
