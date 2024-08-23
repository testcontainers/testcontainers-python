import logging
import pytest

from pytest import MonkeyPatch, LogCaptureFixture

from testcontainers.core.config import TestcontainersConfiguration


@pytest.mark.parametrize("show_warning, update_value", [(True, True), (False, False)])
def test_docker_auth_config(caplog: LogCaptureFixture, show_warning: bool, update_value: bool) -> None:
    monkeypatch = MonkeyPatch()
    logging.captureWarnings(True)
    logging.basicConfig()

    if not show_warning:
        monkeypatch.setattr("testcontainers.core.config.warning", lambda x: {})

    monkeypatch.setenv("DOCKER_AUTH_CONFIG", "some_value")

    config = TestcontainersConfiguration()
    assert config.docker_auth_config == "some_value"
    if show_warning:
        assert caplog.text != ""
    else:
        assert caplog.text == ""

    if update_value:
        config.docker_auth_config = "another_value"
        assert config.docker_auth_config == "another_value"

    if show_warning:
        assert caplog.text != ""
    else:
        assert caplog.text == ""

    monkeypatch.undo()


def test_tc_properties_get_tc_host() -> None:
    config = TestcontainersConfiguration()
    config.tc_properties = {"tc.host": "some_value"}
    assert config.tc_properties_get_tc_host() == "some_value"


def test_timeout() -> None:
    config = TestcontainersConfiguration()
    config.max_tries = 2
    config.sleep_time = 3
    assert config.timeout == 6
