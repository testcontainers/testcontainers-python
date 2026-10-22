import os
import subprocess
import sys
from contextlib import suppress
from time import perf_counter, sleep

import docker
import pytest
from docker import DockerClient
from docker.errors import NotFound

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


@pytest.mark.skipif(
    is_mac(),
    reason="Ryuk container reaping is unreliable on Docker Desktop for macOS due to VM-based container lifecycle handling",
)
@pytest.mark.inside_docker_check
def test_reaper_removes_session_containers_after_interpreter_exit():
    script = (
        "from testcontainers.core.container import DockerContainer\n"
        "container = DockerContainer('hello-world').start()\n"
        "print(container.get_wrapped_container().id)\n"
    )
    child = subprocess.run(
        [sys.executable, "-c", script],
        env={**os.environ, "RYUK_RECONNECTION_TIMEOUT": "1s"},
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert child.returncode == 0, child.stderr
    container_id = child.stdout.strip().splitlines()[-1]

    docker_client = docker.from_env()
    try:
        # The process exited normally without stopping its container: Ryuk must reap it.
        _wait_for_container_removed(docker_client, container_id, timeout=30)
    finally:
        with suppress(NotFound):
            docker_client.containers.get(container_id).remove(force=True)
