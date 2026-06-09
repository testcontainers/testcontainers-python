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

import pytest

from testcontainers.core.container import DockerContainer


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
