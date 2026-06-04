import pytest
from testcontainers.openfga import OpenFGAContainer
from sys import version_info


def test_openfga():
    if version_info < (3, 10):
        with pytest.raises(NotImplementedError):
            _test_openfga()
    else:
        _test_openfga()


def _test_openfga():
    with OpenFGAContainer("openfga/openfga:v1.8.4") as openfga:
        client = openfga.get_client()
        assert client
        assert client.list_stores()
