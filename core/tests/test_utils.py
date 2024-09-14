from pytest import MonkeyPatch, raises, mark

from testcontainers.core import utils


def test_setup_logger() -> None:
    assert utils.setup_logger("test") is not None


@mark.parametrize("platform, expected", [("linux", "linux"), ("linux2", "linux"), ("darwin", "mac"), ("win32", "win")])
def test_os_name(monkeypatch: MonkeyPatch, platform: str, expected: str) -> None:
    assert utils.os_name() is not None
    monkeypatch.setattr("sys.platform", platform)
    assert utils.os_name() == expected


def test_is_mac(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("testcontainers.core.utils.os_name", lambda: "mac")
    assert utils.is_mac()


def test_is_linux(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("testcontainers.core.utils.os_name", lambda: "linux")
    assert utils.is_linux()


def test_is_windows(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("testcontainers.core.utils.os_name", lambda: "win")
    assert utils.is_windows()


def test_is_arm(monkeypatch: MonkeyPatch) -> None:
    assert not utils.is_arm()
    monkeypatch.setattr("platform.machine", lambda: "arm64")
    assert utils.is_arm()
    monkeypatch.setattr("platform.machine", lambda: "aarch64")
    assert utils.is_arm()


def test_inside_container(monkeypatch: MonkeyPatch) -> None:
    assert not utils.inside_container()
    monkeypatch.setattr("os.path.exists", lambda _: True)
    assert utils.inside_container()


def test_raise_for_deprecated_parameters() -> None:
    kwargs = {"key": "value"}
    current = "key"
    replacement = "new_key"
    with raises(ValueError) as e:
        result = utils.raise_for_deprecated_parameter(kwargs, current, replacement)
        assert str(e.value) == "Parameter 'deprecated' is deprecated and should be replaced by 'replacement'."
        assert result == {}
