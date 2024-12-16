import pytest

from testcontainers.mosquitto import MosquittoContainer

VERSIONS = ["1.6.15", "2.0.18"]


@pytest.mark.parametrize("version", VERSIONS)
def test_mosquitto(version):
    with MosquittoContainer(image=f"eclipse-mosquitto:{version}") as container:
        external_port = int(container.get_exposed_port(container.MQTT_PORT))
        print(f"listening on port: {external_port}")


@pytest.mark.parametrize("version", VERSIONS)
def test_mosquitto_client(version):
    with MosquittoContainer(image=f"eclipse-mosquitto:{version}") as container:
        container.get_client()
