import pytest
from testcontainers.cosmosdb._emulator import CosmosDBEmulatorContainer

from testcontainers.core.utils import is_arm


@pytest.mark.skipif(is_arm(), reason="db2 container not available for ARM")
def test_runs():
    with CosmosDBEmulatorContainer(partition_count=1, bind_ports=False) as emulator:
        assert emulator.server_certificate_pem is not None
        assert emulator.get_exposed_port(8081) is not None
