import os

from testcontainers.compose import DockerCompose


def test_can_spawn_service_via_compose():
    compose = DockerCompose(os.path.dirname(__file__))

    try:
        compose.start()
        host = compose.get_service_host("hub", 4444)
        port = compose.get_service_port("hub", 4444)
        assert host == "0.0.0.0"
        assert port == "4444"
    finally:
        compose.stop()
