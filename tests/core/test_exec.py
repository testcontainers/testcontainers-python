"""Behavioral tests for ``DockerContainer.exec``.

The tests in this module are split in two:

* The functions below pin the *current* behavior of ``.exec()`` as it forwards
  ``str`` and ``list[str]`` commands to ``docker-py``'s ``exec_run``. They exist
  to make any future change in interpretation a visible, intentional diff.
* In particular, they nail down a sharp edge: ``docker-py`` tokenizes a ``str``
  command with ``shlex.split`` and never wraps it in a shell. Pipes, redirects,
  and variable expansion are therefore *not* interpreted -- a fact that is easy
  to assume otherwise and was previously untested.
"""

from collections.abc import Iterator
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from docker.models.containers import ExecResult

from testcontainers.core.container import DockerContainer, ExecConfig
from testcontainers.core.exceptions import ContainerStartException

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture(scope="module")
def running_container() -> Iterator[DockerContainer]:
    """A long-lived alpine container to exec against (exec is read-only here)."""
    container = DockerContainer("alpine").with_command("tail -f /dev/null")
    with container:
        yield container


def test_exec_str_command(running_container: DockerContainer) -> None:
    result = running_container.exec("echo hello")
    assert result.exit_code == 0
    assert isinstance(result.output, bytes)
    assert result.output.strip() == b"hello"


def test_exec_list_command(running_container: DockerContainer) -> None:
    result = running_container.exec(["echo", "hello"])
    assert result.exit_code == 0
    assert result.output.strip() == b"hello"


def test_exec_nonzero_exit_code_is_propagated(running_container: DockerContainer) -> None:
    result = running_container.exec(["sh", "-c", "exit 3"])
    assert result.exit_code == 3


def test_str_command_is_tokenized_not_shell_interpreted(running_container: DockerContainer) -> None:
    """A ``str`` command is split with ``shlex``, not run through a shell.

    ``echo a | wc -l`` becomes the argv ``["echo", "a", "|", "wc", "-l"]``, so
    ``echo`` prints the pipe and ``wc`` literally instead of counting lines.
    """
    result = running_container.exec("echo a | wc -l")
    assert result.exit_code == 0
    assert result.output.strip() == b"a | wc -l"


def test_str_command_does_not_redirect(running_container: DockerContainer) -> None:
    result = running_container.exec("echo hi > /tmp/frob")
    assert result.exit_code == 0
    assert result.output.strip() == b"hi > /tmp/frob"


def test_str_command_does_not_expand_variables(running_container: DockerContainer) -> None:
    """No shell means no parameter expansion: ``$HOME`` reaches ``echo`` verbatim."""
    result = running_container.exec("echo $HOME")
    assert result.exit_code == 0
    assert result.output.strip() == b"$HOME"


# --- Pure unit tests for the config -> exec_run kwargs seam (no Docker needed) ---


def test_exec_config_requires_only_command() -> None:
    config = ExecConfig(command=["echo", "hi"])
    assert config.command == ["echo", "hi"]
    assert config.user is None
    assert config.environment is None
    assert config.workdir is None
    assert config.privileged is False


def test_exec_config_is_frozen() -> None:
    config = ExecConfig(command="true")
    with pytest.raises(FrozenInstanceError):
        config.user = "frob"  # type: ignore[misc]


def test_exec_config_supports_dataclasses_replace() -> None:
    base = ExecConfig(command="true")
    derived = replace(base, workdir="/tmp", user="frob")
    assert base.workdir is None  # original untouched
    assert base.user is None
    assert derived.command == "true"
    assert derived.workdir == "/tmp"
    assert derived.user == "frob"


def test_kwargs_defaults_collapse_user_to_docker_sentinel() -> None:
    kwargs = ExecConfig(command=["whoami"]).to_exec_run_kwargs()
    assert kwargs == {
        "cmd": ["whoami"],
        "user": "",  # docker-py's empty-string sentinel, not our None
        "environment": None,
        "workdir": None,
        "privileged": False,
    }


def test_kwargs_forward_str_command_verbatim() -> None:
    # docker-py does its own shlex tokenization; we must not pre-split.
    assert ExecConfig(command="echo a | wc -l").to_exec_run_kwargs()["cmd"] == "echo a | wc -l"


def test_kwargs_pass_through_user_environment_and_privileged() -> None:
    kwargs = ExecConfig(command=["env"], user="frob", environment={"FROB": "243"}, privileged=True).to_exec_run_kwargs()
    assert kwargs["user"] == "frob"
    assert kwargs["environment"] == {"FROB": "243"}
    assert kwargs["privileged"] is True


def test_kwargs_stringify_pathlike_workdir() -> None:
    kwargs = ExecConfig(command=["pwd"], workdir=Path("/tmp/xyzzy")).to_exec_run_kwargs()
    assert kwargs["workdir"] == "/tmp/xyzzy"
    assert isinstance(kwargs["workdir"], str)


def test_kwargs_leave_unset_workdir_as_none() -> None:
    assert ExecConfig(command=["pwd"]).to_exec_run_kwargs()["workdir"] is None


@pytest.fixture
def offline_container(mocker: "MockerFixture") -> DockerContainer:
    """A DockerContainer whose client is mocked away, so exec() can be exercised
    without a running daemon. ``_container`` is wired with a stub ``exec_run``."""
    mocker.patch("testcontainers.core.container.DockerClient")
    return DockerContainer("alpine")


def test_exec_wraps_str_into_config_and_forwards_kwargs(offline_container: DockerContainer) -> None:
    offline_container._container = MagicMock()
    offline_container._container.exec_run.return_value = ExecResult(exit_code=0, output=b"hi")
    result = offline_container.exec("echo hi")
    offline_container._container.exec_run.assert_called_once_with(
        cmd="echo hi", user="", environment=None, workdir=None, privileged=False
    )
    assert result.exit_code == 0
    assert result.output == b"hi"


def test_exec_accepts_exec_config_directly(offline_container: DockerContainer) -> None:
    offline_container._container = MagicMock()
    offline_container._container.exec_run.return_value = ExecResult(exit_code=0, output=b"hi")
    offline_container.exec(ExecConfig(command=["pwd"], workdir=Path("/tmp"), user="frob"))
    offline_container._container.exec_run.assert_called_once_with(
        cmd=["pwd"], user="frob", environment=None, workdir="/tmp", privileged=False
    )


def test_exec_before_start_raises(mocker: "MockerFixture") -> None:
    mocker.patch("testcontainers.core.container.DockerClient")
    with pytest.raises(ContainerStartException):
        DockerContainer("alpine").exec("true")


# --- Integration tests for the new ExecConfig fields (require a Docker daemon) ---


def test_exec_config_workdir_str(running_container: DockerContainer) -> None:
    result = running_container.exec(ExecConfig(command=["pwd"], workdir="/tmp"))
    assert result.exit_code == 0
    assert result.output.strip() == b"/tmp"


def test_exec_config_workdir_accepts_pathlib_path(running_container: DockerContainer) -> None:
    result = running_container.exec(ExecConfig(command=["pwd"], workdir=Path("/tmp")))
    assert result.exit_code == 0
    assert result.output.strip() == b"/tmp"


def test_exec_config_environment(running_container: DockerContainer) -> None:
    result = running_container.exec(ExecConfig(command=["env"], environment={"FROB": "243"}))
    assert result.exit_code == 0
    assert b"FROB=243" in result.output


def test_exec_config_user(running_container: DockerContainer) -> None:
    as_default = running_container.exec(ExecConfig(command=["whoami"]))
    as_nobody = running_container.exec(ExecConfig(command=["whoami"], user="nobody"))
    assert as_default.output.strip() == b"root"
    assert as_nobody.output.strip() == b"nobody"


def test_exec_config_privileged_grants_more_capabilities(running_container: DockerContainer) -> None:
    """A privileged exec receives the full capability set, even though the
    container itself is unprivileged -- so its CapEff strictly exceeds the
    default exec's. We read the effective set straight from procfs."""

    def cap_eff(config: ExecConfig) -> int:
        output = running_container.exec(config).output.decode()
        # /proc/self/status line looks like: "CapEff:\t00000000a80425fb"
        line = next(ln for ln in output.splitlines() if ln.startswith("CapEff:"))
        return int(line.split()[1], 16)

    default_caps = cap_eff(ExecConfig(command=["grep", "CapEff", "/proc/self/status"]))
    privileged_caps = cap_eff(ExecConfig(command=["grep", "CapEff", "/proc/self/status"], privileged=True))
    assert privileged_caps > default_caps
