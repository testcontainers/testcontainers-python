from testcontainers.core.config import TestcontainersConfiguration as TCC, _WARNINGS

from pytest import MonkeyPatch, mark, LogCaptureFixture

import logging


@mark.parametrize("docker_auth_config_env", ["key=value", ""])
@mark.parametrize("warning_dict", [{}, {"key": "value"}, {"DOCKER_AUTH_CONFIG": "TEST"}])
@mark.parametrize("warning_dict_post", [{}, {"key": "value"}, {"DOCKER_AUTH_CONFIG": "TEST"}])
def test_docker_auth_config(
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
    docker_auth_config_env: str,
    warning_dict: dict[str, str],
    warning_dict_post: dict[str, str],
) -> None:
    monkeypatch.setattr("testcontainers.core.config._WARNINGS", warning_dict)
    monkeypatch.setenv("DOCKER_AUTH_CONFIG", docker_auth_config_env)
    caplog.set_level(logging.WARNING)

    config = TCC()
    if not docker_auth_config_env:
        assert config.docker_auth_config == ""
        assert caplog.text == ""
    else:
        assert config.docker_auth_config == docker_auth_config_env

    if "DOCKER_AUTH_CONFIG" in warning_dict:
        assert warning_dict["DOCKER_AUTH_CONFIG"] in caplog.text

    if warning_dict == {}:
        monkeypatch.setattr("testcontainers.core.config._WARNINGS", warning_dict_post)

    config.docker_auth_config = "new_value"
    assert config.docker_auth_config == "new_value"


def test_tc_properties_get_tc_host() -> None:
    config = TCC()
    config.tc_properties = {"tc.host": "some_value"}
    assert config.tc_properties_get_tc_host() == "some_value"


def test_timeout() -> None:
    config = TCC()
    config.max_tries = 2
    config.sleep_time = 3
    assert config.timeout == 6
