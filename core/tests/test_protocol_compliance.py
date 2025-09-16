"""Test protocol compliance for wait strategy targets."""

import pytest
from typing import get_type_hints

from testcontainers.core.waiting_utils import WaitStrategyTarget
from testcontainers.core.container import DockerContainer
from testcontainers.compose.compose import ComposeContainer


def test_docker_container_implements_wait_strategy_target():
    """Test that DockerContainer implements all WaitStrategyTarget protocol methods."""
    container = DockerContainer("hello-world")

    # Check all required methods exist
    assert hasattr(container, "get_container_host_ip")
    assert hasattr(container, "get_exposed_port")
    assert hasattr(container, "get_wrapped_container")
    assert hasattr(container, "get_logs")
    assert hasattr(container, "reload")
    assert hasattr(container, "status")

    # Check method signatures are callable
    assert callable(container.get_container_host_ip)
    assert callable(container.get_exposed_port)
    assert callable(container.get_wrapped_container)
    assert callable(container.get_logs)
    assert callable(container.reload)

    # Status should be a property
    assert isinstance(container.__class__.status, property)


def test_compose_container_implements_wait_strategy_target():
    """Test that ComposeContainer implements all WaitStrategyTarget protocol methods."""
    container = ComposeContainer()

    # Check all required methods exist
    assert hasattr(container, "get_container_host_ip")
    assert hasattr(container, "get_exposed_port")
    assert hasattr(container, "get_wrapped_container")
    assert hasattr(container, "get_logs")
    assert hasattr(container, "reload")
    assert hasattr(container, "status")

    # Check method signatures are callable
    assert callable(container.get_container_host_ip)
    assert callable(container.get_exposed_port)
    assert callable(container.get_wrapped_container)
    assert callable(container.get_logs)
    assert callable(container.reload)

    # Status should be a property
    assert isinstance(container.__class__.status, property)


def test_protocol_typing_compatibility():
    """Test that both classes can be used where WaitStrategyTarget is expected."""

    def function_expecting_protocol(target: WaitStrategyTarget) -> str:
        """A function that expects a WaitStrategyTarget."""
        return "accepted"

    # These should work without type errors (structural typing)
    docker_container = DockerContainer("hello-world")
    compose_container = ComposeContainer()

    # If the classes properly implement the protocol, these should work
    result1 = function_expecting_protocol(docker_container)
    result2 = function_expecting_protocol(compose_container)

    assert result1 == "accepted"
    assert result2 == "accepted"
