from time import perf_counter, sleep

import pytest
from docker import DockerClient
from docker.errors import APIError, NotFound

from testcontainers.core.config import testcontainers_config
from testcontainers.core.container import DockerContainer, Reaper
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


class _FakeResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        self.reason = "Conflict" if status_code == 409 else "Server Error"
        self.url = "http+docker://localhost/containers/ryuk"


class _DeadReaperContainer:
    """Stands in for a ryuk container that died and that Docker is already auto-removing."""

    def __init__(self, status_code: int) -> None:
        self._container = object()
        self._status_code = status_code

    def stop(self) -> None:
        raise APIError("removal of container is already in progress", response=_FakeResponse(self._status_code))


class _FakeSocket:
    closed = False

    def close(self) -> None:
        self.closed = True


def test_delete_instance_treats_removal_in_progress_as_gone(monkeypatch: pytest.MonkeyPatch):
    # https://github.com/testcontainers/testcontainers-python/issues/1125
    dead = Reaper()
    sock = _FakeSocket()
    monkeypatch.setattr(Reaper, "_instance", dead)
    monkeypatch.setattr(Reaper, "_container", _DeadReaperContainer(409))
    monkeypatch.setattr(Reaper, "_socket", sock)

    Reaper.delete_instance()

    assert sock.closed
    assert Reaper._socket is None
    assert Reaper._container is None
    assert Reaper._instance is None

    fresh = Reaper()
    monkeypatch.setattr(Reaper, "_create_instance", classmethod(lambda cls: fresh))
    assert Reaper.get_instance() is fresh


def test_delete_instance_resets_its_state_when_stop_fails(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(Reaper, "_instance", Reaper())
    monkeypatch.setattr(Reaper, "_container", _DeadReaperContainer(500))
    monkeypatch.setattr(Reaper, "_socket", _FakeSocket())

    with pytest.raises(APIError):
        Reaper.delete_instance()

    assert Reaper._socket is None
    assert Reaper._container is None
    assert Reaper._instance is None
