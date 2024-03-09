import json
import urllib

from testcontainers.localstack import LocalStackContainer


def test_docker_run_localstack():
    with LocalStackContainer() as localstack:
        resp = urllib.request.urlopen(f"{localstack.get_url()}/health")
        services = json.loads(resp.read().decode())["services"]

        # Check that all services are running
        assert all(value == "available" for value in services.values())
        # Check that some of the services keys
        assert all(test_service in services for test_service in ["dynamodb", "sns", "sqs"])


def test_localstack_boto3():
    from testcontainers.localstack import LocalStackContainer

    with LocalStackContainer(image="localstack/localstack:2.0.1") as localstack:
        dynamo_client = localstack.get_client("dynamodb")
        tables = dynamo_client.list_tables()
    assert tables["TableNames"] == []
