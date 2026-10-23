from pathlib import Path
from textwrap import dedent
from urllib.request import urlopen

import pytest

from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy, LogMessageWaitStrategy


class TestRealDockerIntegration:
    """Integration tests using real Docker containers."""

    @pytest.mark.parametrize("status_code", [200, 404, 503])
    def test_http_wait_checks_response_body_with_real_container(self, status_code):
        # Keep the status constant so readiness depends on the response body.
        # The first health request is not ready; the second one is.
        server = dedent(
            f"""
            from http.server import BaseHTTPRequestHandler, HTTPServer

            class Handler(BaseHTTPRequestHandler):
                health_requests = 0

                def do_GET(self):
                    if self.path == "/requests":
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(str(Handler.health_requests).encode())
                        return
                    Handler.health_requests += 1
                    body = b"starting" if Handler.health_requests == 1 else b"ready"
                    self.send_response({status_code})
                    self.end_headers()
                    self.wfile.write(body)

            HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
            """
        )
        strategy = (
            HttpWaitStrategy(8080, "/health")
            .for_status_code(status_code)
            .for_response_predicate(lambda body: body == "ready")
            .with_startup_timeout(30)
            .with_poll_interval(0.1)
        )

        with (
            DockerContainer("python:3.12-alpine")
            .with_exposed_ports(8080)
            .with_command(["python", "-u", "-c", server])
            .waiting_for(strategy) as container
        ):
            url = f"http://{container.get_container_host_ip()}:{container.get_exposed_port(8080)}/requests"
            with urlopen(url, timeout=5) as response:
                assert response.read() == b"2"

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
        from pathlib import Path

        from testcontainers.compose import DockerCompose

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
