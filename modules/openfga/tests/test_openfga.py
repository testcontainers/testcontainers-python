from testcontainers.openfga import OpenFGAContainer

def test_openfga():
    with OpenFGAContainer("openfga/openfga:v1.8.4") as openfga:
        client = openfga.get_client()
        assert client
        assert client.list_stores()
