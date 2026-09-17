from unittest.mock import patch

from testcontainers.community.trino import TrinoContainer


def test_get_connection_url_uses_mapped_host_port():
    # Regression test for #1111: the URL must carry the mapped host port,
    # not the container-internal one.
    container = TrinoContainer()
    with (
        patch.object(TrinoContainer, "get_container_host_ip", return_value="localhost"),
        patch.object(TrinoContainer, "get_exposed_port", return_value=58092) as exposed,
    ):
        assert container.get_connection_url() == "trino://test@localhost:58092"
        exposed.assert_called_once_with(8080)
