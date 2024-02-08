import pytest

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


def test_raise_timeout():
    with pytest.raises(TimeoutError):
        with DockerContainer("alpine").with_command("sleep 2") as container:
            wait_for_logs(container, "Hello from Docker!", timeout=1e-3)


def test_wait_for_hello():
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")


def test_can_get_logs():
    with DockerContainer("hello-world") as container:
        wait_for_logs(container, "Hello from Docker!")
        stdout, stderr = container.get_logs()
        assert stdout, 'There should be something on stdout'


@pytest.mark.parametrize(
    "init_attr,init_value,class_attr,stored_value",
    [
        ("command", "ps", "_command", "ps"),
        ("env", {"e1": "v1"}, "env", {"e1": "v1"}),
        ("name", "foo-bar", "_name", "foo-bar"),
        ("ports", [22, 80], "ports", {22: None, 80: None}),
        (
            "volumes",
            [("/tmp", "/tmp2", "ro")],
            "volumes",
            {"/tmp": {"bind": "/tmp2", "mode": "ro"}},
        ),
    ],
)
def test_attribute(init_attr, init_value, class_attr, stored_value):
    """Test that the attributes set through the __init__ function are properly stored."""
    with DockerContainer("ubuntu", **{init_attr: init_value}) as container:
        assert getattr(container, class_attr) == stored_value
