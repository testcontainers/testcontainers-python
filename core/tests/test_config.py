from testcontainers.core.config import TestcontainersConfiguration as TCC


def test_docker_auth_config() -> None:
    config = TCC()
    assert config.docker_auth_config is None
    config.docker_auth_config = "value"
    assert config.docker_auth_config == "value"


def test_tc_properties_get_tc_host() -> None:
    config = TCC()
    config.tc_properties = {"tc.host": "some_value"}
    assert config.tc_properties_get_tc_host() == "some_value"


def test_timeout() -> None:
    config = TCC()
    config.max_tries = 2
    config.sleep_time = 3
    assert config.timeout == 6
