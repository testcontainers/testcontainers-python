import re
import pytest

from testcontainers.aws import AWSLambdaContainer
from testcontainers.aws.aws_lambda import RIE_PATH

DOCKER_FILE_PATH = "./modules/aws/tests/lambda_sample"
IMAGE_TAG = "lambda:test"


def test_aws_lambda_container():
    with AWSLambdaContainer(path=DOCKER_FILE_PATH, port=8080, tag=IMAGE_TAG, image_cleanup=False) as func:
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


def test_aws_lambda_container_no_tag():
    with AWSLambdaContainer(path=DOCKER_FILE_PATH, image_cleanup=True) as func:
        response = func.send_request(data={"payload": "test"})
        assert response.status_code == 200


def test_aws_lambda_container_no_path():
    with pytest.raises(TypeError):
        with AWSLambdaContainer(port=8080, tag=IMAGE_TAG, image_cleanup=True):
            pass
