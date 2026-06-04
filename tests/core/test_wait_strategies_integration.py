import tempfile
import time
from pathlib import Path

import pytest

from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy


class TestRealDockerIntegration:
    """Integration tests using real Docker containers."""

    def test_log_message_wait_strategy_with_real_container(self):
        """Test LogMessageWaitStrategy with a real container that outputs known logs."""
        strategy = LogMessageWaitStrategy("Hello from Docker!")

        with DockerContainer("hello-world").waiting_for(strategy) as container:
            # If we get here, the strategy worked
            assert container.get_wrapped_container() is not None

    def test_wait_strategy_timeout_with_real_container(self):
        """Test that wait strategies properly timeout with real containers."""
        # Use a very short timeout with a condition that won't be met
        strategy = LogMessageWaitStrategy("this_message_will_never_appear").with_startup_timeout(2)

        with pytest.raises(TimeoutError):
            with DockerContainer("alpine:latest").with_command("sleep 10").waiting_for(strategy):
                pass  # Should not reach here


class TestDockerComposeIntegration:
    """Integration tests for wait strategies with Docker Compose."""

    def test_compose_service_wait_strategies(self):
        """Test that wait strategies work with Docker Compose services."""
        from testcontainers.compose import DockerCompose
        import tempfile
        from pathlib import Path

        # Use basic_multiple fixture with two alpine services that output logs
        compose = DockerCompose(
            context=Path(__file__).parent / "compose_fixtures" / "basic_multiple",
            compose_file_name="docker-compose.yaml",
        )

        # Configure wait strategies for both services
        # Wait for the date output that these containers produce
        compose.waiting_for(
            {
                "alpine1": LogMessageWaitStrategy("202").with_startup_timeout(30),  # Date includes year 202X
                "alpine2": LogMessageWaitStrategy("202").with_startup_timeout(30),  # Date includes year 202X
            }
        )

        with compose:
            # Verify both services are running
            container1 = compose.get_container("alpine1")
            container2 = compose.get_container("alpine2")

            assert container1.State == "running"
            assert container2.State == "running"

            # Verify logs contain expected patterns
            logs1 = container1.get_logs()
            logs2 = container2.get_logs()

            # Both containers should have date output (which contains "202" for year 202X)
            assert any(b"202" in log for log in logs1)
            assert any(b"202" in log for log in logs2)

    def test_compose_wait_strategy_timeout(self):
        """Test that compose wait strategies properly timeout."""
        from testcontainers.compose import DockerCompose
        from pathlib import Path

        compose = DockerCompose(
            context=Path(__file__).parent / "compose_fixtures" / "basic", compose_file_name="docker-compose.yaml"
        )

        # Use a wait strategy that will never succeed with very short timeout
        compose.waiting_for(
            {"alpine": LogMessageWaitStrategy("this_message_will_never_appear").with_startup_timeout(2)}
        )

        with pytest.raises(TimeoutError):
            with compose:
                pass  # Should not reach here
