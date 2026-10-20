from socket import socket, socketpair
from urllib.parse import parse_qs

import pytest
from pytest_mock import MockerFixture

from testcontainers.core.container import Reaper
from testcontainers.core.labels import LABEL_SESSION_ID, SESSION_ID


def test_register_filters_handles_fragmented_acknowledgements(mocker: MockerFixture):
    connection = mocker.Mock(spec=socket)
    connection.gettimeout.return_value = 1.0
    connection.recv.side_effect = [b"A", b"C", b"K\n", b"ACK\n"]
    mocker.patch.object(Reaper, "_socket", connection)
    reaper = Reaper()

    reaper.register_labels_filter({LABEL_SESSION_ID: SESSION_ID})
    labels = {"com.docker.compose.project": "test-project", "custom": "spaces & equals= and +"}
    reaper.register_labels_filter(labels)

    messages = [call.args[0].decode() for call in connection.sendall.call_args_list]
    assert all(message.endswith("\n") for message in messages)
    assert parse_qs(messages[0].strip()) == {"label": [f"{LABEL_SESSION_ID}={SESSION_ID}"]}
    assert parse_qs(messages[1].strip()) == {"label": [f"{key}={value}" for key, value in labels.items()]}
    assert connection.settimeout.call_args.args == (1.0,)


@pytest.mark.parametrize("response", [b"", b"NOPE", TimeoutError("no acknowledgement")])
def test_failed_registration_does_not_reuse_a_late_ack_or_close_the_session(mocker: MockerFixture, response):
    connection = mocker.Mock(spec=socket)
    connection.gettimeout.return_value = 1.0
    connection.recv.side_effect = [response, b"ACK\n"]
    mocker.patch.object(Reaper, "_socket", connection)
    reaper = Reaper()

    with pytest.raises(OSError):
        reaper.register_labels_filter({"project": "first"})
    with pytest.raises(ConnectionError, match="unavailable"):
        reaper.register_labels_filter({"project": "second"})

    assert connection.sendall.call_count == 1
    connection.close.assert_not_called()
    assert connection.settimeout.call_args.args == (1.0,)


def test_registration_has_an_overall_deadline(mocker: MockerFixture):
    connection = mocker.Mock(spec=socket)
    connection.gettimeout.return_value = 1.0
    connection.recv.return_value = b"A"
    mocker.patch.object(Reaper, "_socket", connection)
    mocker.patch("testcontainers.core.container.monotonic", side_effect=[0, 1, 11])

    with pytest.raises(TimeoutError, match="Timed out"):
        Reaper().register_labels_filter({"project": "slow"})
    assert connection.recv.call_count == 1


def test_empty_filter_is_rejected(mocker: MockerFixture):
    connection = mocker.Mock(spec=socket)
    mocker.patch.object(Reaper, "_socket", connection)
    with pytest.raises(ValueError, match="at least one label"):
        Reaper().register_labels_filter({})
    connection.sendall.assert_not_called()


def test_registration_requires_a_connection(mocker: MockerFixture):
    mocker.patch.object(Reaper, "_socket", None)
    with pytest.raises(ConnectionError, match="unavailable"):
        Reaper().register_labels_filter({"project": "missing"})


def test_unresponsive_peer_times_out_without_closing_the_connection(monkeypatch: pytest.MonkeyPatch):
    connection, peer = socketpair()
    with connection, peer:
        connection.settimeout(1)
        monkeypatch.setattr(Reaper, "_socket", connection)
        monkeypatch.setattr(Reaper, "_ACK_TIMEOUT", 0.05)
        reaper = Reaper()
        with pytest.raises(TimeoutError):
            reaper.register_labels_filter({"project": "unacknowledged"})
        assert connection.gettimeout() == 1
        assert connection.fileno() != -1
        peer.sendall(b"ACK\n")
        with pytest.raises(ConnectionError, match="unavailable"):
            reaper.register_labels_filter({"project": "another"})


@pytest.mark.parametrize("failure", [False, True])
def test_initial_session_registration_is_acknowledged(mocker: MockerFixture, failure: bool):
    container = mocker.MagicMock()
    container.get_container_host_ip.return_value = "localhost"
    container.get_exposed_port.return_value = 12345
    constructor = mocker.patch("testcontainers.core.container.DockerContainer")
    builder = constructor.return_value
    for method in ("with_name", "with_exposed_ports", "with_volume_mapping", "with_kwargs", "with_env"):
        getattr(builder, method).return_value = builder
    builder.start.return_value = container
    connection = mocker.patch("testcontainers.core.container.socket").return_value
    connection.gettimeout.return_value = 1.0
    connection.recv.side_effect = [b""] if failure else [b"ACK\n"]
    mocker.patch.object(Reaper, "_container", None)
    mocker.patch.object(Reaper, "_instance", None)
    mocker.patch.object(Reaper, "_socket", None)
    register_exit = mocker.patch("testcontainers.core.container.atexit").register

    if failure:
        with pytest.raises(ConnectionError):
            Reaper.get_instance()
        assert Reaper._instance is None
        assert Reaper._socket is None
        container.stop.assert_called_once()
        register_exit.assert_not_called()
    else:
        instance = Reaper.get_instance()
        assert instance is Reaper.get_instance()
        container.stop.assert_not_called()
        register_exit.assert_called_once_with(Reaper.delete_instance)

    message = connection.sendall.call_args.args[0].decode().strip()
    assert parse_qs(message) == {"label": [f"{LABEL_SESSION_ID}={SESSION_ID}"]}
    connection.recv.assert_called_once()
