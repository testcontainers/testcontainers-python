import pytest
from testcontainers.community.cosmosdb._emulator import CosmosDBEmulatorContainer


def test_runs():
    with CosmosDBEmulatorContainer(partition_count=1, bind_ports=False) as emulator:
        assert emulator.server_certificate_pem is not None
        assert emulator.get_exposed_port(8081) is not None
