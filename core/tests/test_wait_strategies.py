import itertools
import re
import time
import typing
from datetime import timedelta
from unittest.mock import Mock, patch

import pytest

from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from testcontainers.core.waiting_utils import WaitStrategy

if typing.TYPE_CHECKING:
    from testcontainers.core.waiting_utils import WaitStrategyTarget


class ConcreteWaitStrategy(WaitStrategy):
    """Concrete implementation for testing abstract base class."""

    def wait_until_ready(self, container: "WaitStrategyTarget") -> None:
        # Simple implementation that just waits a bit
        time.sleep(0.1)


class TestWaitStrategy:
    """Test the base WaitStrategy class."""

    def test_wait_strategy_initialization(self):
        strategy = ConcreteWaitStrategy()
        assert strategy._startup_timeout > 0
        assert strategy._poll_interval > 0

    @pytest.mark.parametrize(
        "timeout_value,expected_seconds",
        [
            (30, 30),
            (timedelta(seconds=45), 45),
            (60, 60),
            (timedelta(minutes=2), 120),
        ],
        ids=[
            "timeout_int_30_seconds",
            "timeout_timedelta_45_seconds",
            "timeout_int_60_seconds",
            "timeout_timedelta_2_minutes",
        ],
    )
    def test_with_startup_timeout(self, timeout_value, expected_seconds):
        strategy = ConcreteWaitStrategy()
        result = strategy.with_startup_timeout(timeout_value)
        assert result is strategy
        assert strategy._startup_timeout == expected_seconds

    @pytest.mark.parametrize(
        "interval_value,expected_seconds",
        [
            (2.5, 2.5),
            (timedelta(seconds=3), 3.0),
            (0.1, 0.1),
            (timedelta(milliseconds=500), 0.5),
        ],
        ids=[
            "interval_float_2_5_seconds",
            "interval_timedelta_3_seconds",
            "interval_float_0_1_seconds",
            "interval_timedelta_500_milliseconds",
        ],
    )
    def test_with_poll_interval(self, interval_value, expected_seconds):
        strategy = ConcreteWaitStrategy()
        result = strategy.with_poll_interval(interval_value)
        assert result is strategy
        assert strategy._poll_interval == expected_seconds

    def test_abstract_method(self):
        # Test that abstract base class cannot be instantiated
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            WaitStrategy()  # type: ignore[abstract]


class TestLogMessageWaitStrategy:
    """Test the LogMessageWaitStrategy class."""

    @pytest.mark.parametrize(
        "message,times,predicate_streams_and",
        [
            ("test message", 1, False),
            (re.compile(r"test\d+"), 1, False),
            ("test", 3, False),
            ("test", 1, True),
            ("ready", 2, True),
        ],
        ids=[
            "simple_string_message",
            "regex_pattern_message",
            "message_with_times_3",
            "message_with_predicate_streams_and_true",
            "ready_message_with_times_and_predicate",
        ],
    )
    def test_log_message_wait_strategy_initialization(self, message, times, predicate_streams_and):
        strategy = LogMessageWaitStrategy(message, times=times, predicate_streams_and=predicate_streams_and)

        if isinstance(message, str):
            assert strategy._message.pattern == message
        else:
            assert strategy._message is message

        assert strategy._times == times
        assert strategy._predicate_streams_and is predicate_streams_and

    @pytest.mark.parametrize(
        "container_logs,expected_message,should_succeed",
        [
            ((b"test message", b""), "test message", True),
            ((b"", b"test message"), "test message", True),
            ((b"no match", b""), "test message", False),
            ((b"test123", b""), re.compile(r"test\d+"), True),
            ((b"test", b""), re.compile(r"test\d+"), False),
        ],
        ids=[
            "stdout_contains_message_success",
            "stderr_contains_message_success",
            "no_message_match_failure",
            "regex_pattern_match_success",
            "regex_pattern_no_match_failure",
        ],
    )
    @patch("time.time")
    @patch("time.sleep")
    def test_wait_until_ready(self, mock_sleep, mock_time, container_logs, expected_message, should_succeed):
        strategy = LogMessageWaitStrategy(expected_message)
        mock_container = Mock()
        mock_container.get_logs.return_value = container_logs
        # Mock the wrapped container to simulate a running container
        mock_wrapped = Mock()
        mock_wrapped.status = "running"
        mock_wrapped.reload.return_value = None
        mock_container.get_wrapped_container.return_value = mock_wrapped
        # Configure time mock to simulate timeout for failure cases
        if should_succeed:
            mock_time.side_effect = [0, 1]
        else:
            mock_time.side_effect = itertools.count(start=0, step=1)
        if should_succeed:
            strategy.wait_until_ready(mock_container)
            mock_container.get_logs.assert_called_once()
        else:
            with pytest.raises(TimeoutError):
                strategy.wait_until_ready(mock_container)
