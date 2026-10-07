import json
import os
import subprocess
import sys
from contextlib import ExitStack, suppress
from pathlib import Path
from time import monotonic, sleep
from uuid import uuid4

import docker
import pytest
from docker.errors import DockerException, NotFound
from pytest_mock import MockerFixture

from testcontainers.compose import DockerCompose
from testcontainers.core.config import testcontainers_config
from testcontainers.core.container import DockerContainer, Reaper
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.utils import is_mac

FIXTURES = Path(__file__).parent / "compose_fixtures"

_skip_if_mac_ryuk = pytest.mark.skipif(
    is_mac(),
    reason="Ryuk startup and cleanup are unreliable on Docker Desktop for macOS",
)


@pytest.mark.parametrize("enabled,disabled", [(False, False), (True, False), (True, True)])
def test_compose_ryuk_registration_and_command_identity(
    mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, enabled: bool, disabled: bool
):
    monkeypatch.setattr(testcontainers_config, "ryuk_disabled", disabled)
    get_reaper = mocker.patch.object(Reaper, "get_instance")
    delete_reaper = mocker.patch.object(Reaper, "delete_instance")
    compose = DockerCompose(
        ".",
        ryuk=enabled,
        docker_command_path="docker",
        pull=True,
        compose_file_name=["compose.yaml", "override.yaml"],
        profiles=["test"],
        env_file="test.env",
        services=["database"],
    )
    events = []
    get_reaper.return_value.register_labels_filter.side_effect = lambda labels: events.append(("filter", labels))
    run = mocker.patch.object(
        compose, "_run_command", side_effect=lambda **kwargs: events.append(("command", kwargs["cmd"]))
    )
    base = compose.docker_compose_command()[:]
    compose.start()
    compose.stop()
    compose.start()

    assert compose.docker_compose_command() == base
    assert [call.kwargs["cmd"] for call in run.call_args_list] == [
        [*base, "pull"],
        [*base, "up", "--wait", "database"],
        [*base, "down", "--volumes", "database"],
        [*base, "pull"],
        [*base, "up", "--wait", "database"],
    ]
    if enabled:
        assert base[:3] == ["docker", "compose", "--project-name"]
        project = base[3]
        assert DockerCompose(".", ryuk=True, docker_command_path="docker").docker_compose_command()[3] != project
    else:
        assert "--project-name" not in base
    if enabled and not disabled:
        assert events[0] == ("filter", {"com.docker.compose.project": project})
        assert get_reaper.call_count == 2
    else:
        get_reaper.assert_not_called()
    delete_reaper.assert_not_called()


@pytest.mark.parametrize("fail_start", [False, True])
def test_ryuk_failure_prevents_compose_up(mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, fail_start: bool):
    monkeypatch.setattr(testcontainers_config, "ryuk_disabled", False)
    get_reaper = mocker.patch.object(Reaper, "get_instance")
    failing_call = get_reaper if fail_start else get_reaper.return_value.register_labels_filter
    failing_call.side_effect = ConnectionError("Ryuk unavailable")
    compose = DockerCompose(".", ryuk=True, docker_command_path="docker")
    run = mocker.patch.object(compose, "_run_command")
    with pytest.raises(ConnectionError, match="Ryuk unavailable"):
        compose.start()
    run.assert_not_called()


@pytest.mark.parametrize("ryuk_removed", [False, True])
def test_cleanup_timeout_reports_remaining_resources(mocker: MockerFixture, ryuk_removed: bool):
    client = mocker.Mock(spec=docker.DockerClient)
    container = mocker.Mock(id="container-id", status="running")
    container.name = "service"
    network = mocker.Mock(id="network-id")
    network.name = "project-network"
    volume = mocker.Mock()
    volume.name = "project-volume"
    client.containers.list.return_value = [container]
    client.networks.list.return_value = [network]
    client.volumes.list.return_value = [volume]
    if ryuk_removed:
        client.containers.get.side_effect = NotFound("Ryuk already removed")
    else:
        client.containers.get.return_value.logs.return_value = b"cleanup failed"

    with pytest.raises(TimeoutError) as exc:
        _wait_for_project_removed(client, {"project": "test-project", "ryuk": "ryuk-id"}, timeout=0)

    message = str(exc.value)
    for detail in ("test-project", "container-id", "service", "running", "network-id", "project-volume"):
        assert detail in message
    assert ("Unavailable:" if ryuk_removed else "cleanup failed") in message


@pytest.fixture
def compose_ryuk_resources(monkeypatch: pytest.MonkeyPatch):
    with ExitStack() as cleanup:
        client = DockerClient().client
        cleanup.callback(client.close)
        suffix = uuid4().hex
        # Use the configured SDK client without adding Testcontainers ownership labels.
        volume = client.volumes.create(name=f"tc-ryuk-external-{suffix}")
        cleanup.callback(volume.remove)
        network = client.networks.create(name=f"tc-ryuk-external-{suffix}")
        cleanup.callback(network.remove)
        assert network.name is not None
        monkeypatch.setenv("TC_RYUK_EXTERNAL_VOLUME", volume.name)
        monkeypatch.setenv("TC_RYUK_EXTERNAL_NETWORK", network.name)
        monkeypatch.setenv("COMPOSE_PROJECT_NAME", f"tc-ryuk-unrelated-{suffix}")
        yield client, volume, network


@pytest.fixture
def fresh_reaper():
    Reaper.delete_instance()
    try:
        yield
    finally:
        Reaper.delete_instance()


@_skip_if_mac_ryuk
def test_compose_ryuk_isolation_reuse_and_retention(compose_ryuk_resources, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(testcontainers_config, "ryuk_disabled", False)
    client, external_volume, external_network = compose_ryuk_resources
    first = DockerCompose(FIXTURES / "ryuk", ryuk=True, keep_volumes=True)
    second = DockerCompose(FIXTURES / "ryuk", ryuk=True)
    try:
        with first:
            reaper = Reaper.get_instance()
            first_id = first.get_container().ID
            first_project = first.get_container().Project
            first.exec_in_container(["sh", "-c", "echo retained > /data/value"])
            with second:
                assert Reaper.get_instance() is reaper
                assert second.get_container().Project != first_project
                assert second.get_container().ID != first_id
            assert first.get_container().ID == first_id
            assert Reaper.get_instance() is reaper

        # Reusing the same object retains its project and its data.
        with first:
            assert first.get_container().Project == first_project
            assert first.exec_in_container(["cat", "/data/value"])[0].strip() == "retained"
        first.stop()
        assert not client.containers.list(all=True, filters={"label": f"com.docker.compose.project={first_project}"})
        assert not client.volumes.list(filters={"label": f"com.docker.compose.project={first_project}"})
        assert client.volumes.get(external_volume.name)
        assert client.networks.get(external_network.id)
    finally:
        first.stop()
        second.stop()


@_skip_if_mac_ryuk
def test_compose_reuses_reaper_started_by_docker_container(
    fresh_reaper, compose_ryuk_resources, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(testcontainers_config, "ryuk_disabled", False)
    assert Reaper._instance is None
    with DockerContainer("alpine:3.20", command="sleep 300") as ordinary:
        reaper = Reaper._instance
        assert reaper is not None
        with DockerCompose(FIXTURES / "ryuk", ryuk=True):
            assert Reaper.get_instance() is reaper
        container = ordinary.get_wrapped_container()
        container.reload()
        assert container.status == "running"
        assert Reaper.get_instance() is reaper


@_skip_if_mac_ryuk
@pytest.mark.parametrize("scenario", ["running", "retained", "partial"])
def test_compose_ryuk_cleans_up_after_process_kill(compose_ryuk_resources, tmp_path: Path, scenario: str):
    client, external_volume, external_network = compose_ryuk_resources
    unrelated = DockerCompose(FIXTURES / "ryuk")
    ready = tmp_path / "ready.json"
    child = None
    state = None
    env = dict(os.environ, TESTCONTAINERS_RYUK_DISABLED="false", RYUK_RECONNECTION_TIMEOUT="1s")
    try:
        with unrelated:
            unrelated_id = unrelated.get_container().ID
            with (tmp_path / "child.log").open("w+") as log:
                child = subprocess.Popen(
                    [sys.executable, str(FIXTURES / "ryuk" / "start_compose.py"), str(ready), scenario],
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )
                deadline = monotonic() + 120
                while not ready.exists():
                    if child.poll() is not None or monotonic() >= deadline:
                        log.seek(0)
                        pytest.fail(f"Compose child did not become ready:\n{log.read()}")
                    sleep(0.1)
                state = json.loads(ready.read_text())
                filters = {"label": f"com.docker.compose.project={state['project']}"}
                assert client.containers.list(all=True, filters=filters)
                assert client.networks.list(filters=filters)
                assert client.volumes.list(filters=filters)
                assert client.containers.get(state["ryuk"])
                child.kill()
                child.wait(timeout=10)

                _wait_for_project_removed(client, state)

                assert client.containers.get(unrelated_id).status == "running"
                assert client.volumes.get(external_volume.name)
                assert client.networks.get(external_network.id)
    finally:
        if child is not None and child.poll() is None:
            child.kill()
            child.wait(timeout=10)
        if state is None and ready.exists():
            state = json.loads(ready.read_text())
        if state is None and ready.with_suffix(".state.json").exists():
            state = json.loads(ready.with_suffix(".state.json").read_text())
        if state is not None:
            _remove_child_resources(client, state)


def _wait_for_project_removed(client: docker.DockerClient, state: dict[str, str], timeout: float = 60) -> None:
    filters: dict[str, str | list[str] | bool] = {"label": f"com.docker.compose.project={state['project']}"}
    deadline = monotonic() + timeout
    while True:
        containers = client.containers.list(all=True, filters=filters)
        networks = client.networks.list(filters=filters)
        volumes = client.volumes.list(filters=filters)
        if not (containers or networks or volumes):
            return
        if monotonic() >= deadline:
            try:
                ryuk_logs = client.containers.get(state["ryuk"]).logs(tail=100).decode("utf-8", errors="replace")
            except DockerException as exc:
                ryuk_logs = f"Unavailable: {exc}"
            raise TimeoutError(
                f"Ryuk did not clean up project {state['project']} within {timeout}s.\n"
                f"Containers (id, name, status): {[(c.id, c.name, c.status) for c in containers]}\n"
                f"Networks (id, name): {[(n.id, n.name) for n in networks]}\n"
                f"Volumes: {[v.name for v in volumes]}\n"
                f"Ryuk logs:\n{ryuk_logs}"
            )
        sleep(0.2)


def _remove_child_resources(client: docker.DockerClient, state: dict[str, str]) -> None:
    # Only remove resources belonging to this child's generated project.
    filters: dict[str, str | list[str] | bool] = {"label": f"com.docker.compose.project={state['project']}"}
    for container in client.containers.list(all=True, filters=filters):
        with suppress(NotFound):
            container.remove(force=True, v=True)
    for network in client.networks.list(filters=filters):
        with suppress(NotFound):
            network.remove()
    for volume in client.volumes.list(filters=filters):
        with suppress(NotFound):
            volume.remove()
    with suppress(NotFound):
        client.containers.get(state["ryuk"]).remove(force=True)
