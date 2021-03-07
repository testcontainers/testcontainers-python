import json
import urllib

from testcontainers.localstack import LocalStackContainer


def test_docker_run_localstack():
    config = LocalStackContainer()
    with config as localstack:
        resp = urllib.request.urlopen('{}/health'.format(localstack.get_url()))
        services = json.loads(resp.read().decode())['services']

        # Check that all services are running
        assert all(value == 'running' for value in services.values())
        # Check that some of the services keys
        assert all(test_service in services.keys() for test_service in ['dynamodb', 'sns', 'sqs'])
