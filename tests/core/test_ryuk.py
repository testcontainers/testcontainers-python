import socket
import threading
from time import perf_counter, sleep

import pytest
from docker import DockerClient
from docker.errors import NotFound

from testcontainers.core.config import testcontainers_config
from testcontainers.core.container import DockerContainer, Reaper
from testcontainers.core.labels import LABEL_SESSION_ID, SESSION_ID
from testcontainers.core.utils import is_mac
from testcontainers.core.waiting_utils import wait_for_logs


def _wait_for_container_removed(client: DockerClient, container_id: str, timeout: float = 60) -> None:
    """Poll until a container is fully removed (raises NotFound)."""
    start = perf_counter()
    while perf_counter() - start < timeout:
        try:
            client.containers.get(container_id)
        except NotFound:
            return
        sleep(0.5)

    try:
        c = client.containers.get(container_id)
        name = c.name
        status = c.status
        started_at = c.attrs.get("State", {}).get("StartedAt", "unknown")
        detail = f"name={name}, status={status}, started_at={started_at}"
    except NotFound:
        detail = "container disappeared just after timeout"
    raise TimeoutError(f"Container {container_id} was not removed within {timeout}s ({detail})")


@pytest.mark.skipif(
    is_mac(),
    reason="Ryuk container reaping is unreliable on Docker Desktop for macOS due to VM-based container lifecycle handling",
)
@pytest.mark.inside_docker_check
def test_wait_for_reaper(monkeypatch: pytest.MonkeyPatch):
    Reaper.delete_instance()
    monkeypatch.setattr(testcontainers_config, "ryuk_reconnection_timeout", "0.1s")
    container = DockerContainer("hello-world")
    container.start()

    docker_client = container.get_docker_client().client

    container_id = container.get_wrapped_container().short_id
    rc = Reaper._container
    assert rc
    reaper_id = rc.get_wrapped_container().short_id

    assert docker_client.containers.get(container_id) is not None
    assert docker_client.containers.get(reaper_id) is not None

    wait_for_logs(container, "Hello from Docker!")

    rs = Reaper._socket
    assert rs
    rs.close()

    # Ryuk will reap containers then auto-remove itself.
    # Wait for the reaper container to disappear and once it's gone, all labeled containers are guaranteed reaped.
    _wait_for_container_removed(docker_client, reaper_id)

    # Verify both containers were reaped
    with pytest.raises(NotFound):
        docker_client.containers.get(container_id)
    with pytest.raises(NotFound):
        docker_client.containers.get(reaper_id)

    # Cleanup Ryuk class fields after manual Ryuk shutdown
    Reaper.delete_instance()


@pytest.mark.skipif(
    is_mac(), reason="Ryuk disabling behavior is unreliable on Docker Desktop for macOS due to Docker socket emulation"
)
@pytest.mark.inside_docker_check
def test_container_without_ryuk(monkeypatch: pytest.MonkeyPatch):
    Reaper.delete_instance()
    monkeypatch.setattr(testcontainers_config, "ryuk_disabled", True)
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")
        assert Reaper._instance is None


@pytest.mark.inside_docker_check
def test_ryuk_is_reused_in_same_process():
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")
        reaper_instance = Reaper._instance

    assert reaper_instance is not None

    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")
        assert reaper_instance is Reaper._instance


def _serve(connections: list) -> tuple[str, int, list]:
    """Serve one scripted behaviour per incoming connection on a local port.

    Each entry is "reset" (accept and close without reading, like docker-proxy before Ryuk is up),
    "silent" (read the line but never answer) or "ack" (answer like Ryuk).
    """
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen()
    received: list = []

    def run() -> None:
        for behaviour in connections:
            conn, _ = server.accept()
            with conn:
                if behaviour == "reset":
                    continue
                received.append(conn.recv(1024))
                if behaviour == "ack":
                    conn.sendall(b"ACK\n")
                    conn.recv(1024)  # keep the connection open until the client closes it
                else:
                    # Wait for the client to time out and close, so the next connection is accepted right away.
                    while conn.recv(1024):
                        pass
        server.close()

    threading.Thread(target=run, daemon=True).start()
    host, port = server.getsockname()
    return host, port, received


def test_reaper_retries_until_ryuk_acknowledges_the_filter():
    # https://github.com/testcontainers/testcontainers-python/issues/1114
    host, port, received = _serve(["reset", "silent", "ack"])
    s = Reaper._connect_and_register(host, port, retry_delay=0.01, reply_timeout=0.2)
    try:
        assert received[-1] == f"label={LABEL_SESSION_ID}={SESSION_ID}\r\n".encode()
        assert len(received) == 2
    finally:
        s.close()


def test_reaper_raises_when_ryuk_never_acknowledges():
    host, port, _ = _serve(["reset", "reset"])
    with pytest.raises(OSError):
        Reaper._connect_and_register(host, port, timeout=0.5, retry_delay=0.01)


def test_reaper_gives_up_after_the_timeout():
    # A peer that accepts and never answers must not block for longer than the timeout and one attempt.
    host, port, _ = _serve(["silent"] * 100)
    start = perf_counter()
    with pytest.raises(OSError):
        Reaper._connect_and_register(host, port, timeout=0.5, retry_delay=0.01, reply_timeout=0.2)
    assert perf_counter() - start < 2


@pytest.mark.parametrize("fail_in", ["start", "register"])
def test_reaper_removes_its_container_when_setup_fails(monkeypatch: pytest.MonkeyPatch, fail_in: str):
    Reaper.delete_instance()
    seen: dict = {}

    def fake_start(self: DockerContainer) -> DockerContainer:
        seen["wait"] = self._wait_strategy
        self._container = object()  # set once create() has run, before the wait
        if fail_in == "start":
            raise TimeoutError("Ryuk did not log Started")
        return self

    def fake_stop(self: DockerContainer, **kwargs: object) -> None:
        seen["stopped"] = True

    def fail_register(host: str, port: int) -> socket.socket:
        raise ConnectionResetError("no ACK")

    monkeypatch.setattr("testcontainers.core.container.DockerClient", lambda **kwargs: None)
    monkeypatch.setattr(DockerContainer, "start", fake_start)
    monkeypatch.setattr(DockerContainer, "stop", fake_stop)
    monkeypatch.setattr(DockerContainer, "get_container_host_ip", lambda self: "127.0.0.1")
    monkeypatch.setattr(DockerContainer, "get_exposed_port", lambda self, port: "8080")
    monkeypatch.setattr(Reaper, "_connect_and_register", staticmethod(fail_register))

    with pytest.raises((TimeoutError, ConnectionResetError)):
        Reaper.get_instance()

    assert seen.get("stopped")
    assert Reaper._container is None
    assert Reaper._instance is None
    # The wait is set before start(), and it matches the log line of old and new Ryuk versions.
    pattern = seen["wait"]._message
    assert pattern.search("Started!")
    assert pattern.search("level=INFO msg=Started address=[::]:8080")
    assert not pattern.search("Starting")
