"""
Tests for the telemetry module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import time

from blender_mcp.telemetry import (
    TelemetryCollector,
    TelemetryEvent,
    EventType,
    get_telemetry,
    record_tool_usage,
    record_startup,
    is_telemetry_enabled,
)


@pytest.fixture
def reset_telemetry():
    """Reset global telemetry between tests."""
    import blender_mcp.telemetry
    original = blender_mcp.telemetry._telemetry_collector
    blender_mcp.telemetry._telemetry_collector = None
    yield
    blender_mcp.telemetry._telemetry_collector = original


class TestTelemetryEvent:
    """Tests for TelemetryEvent dataclass."""

    def test_create_event(self):
        """Test creating a telemetry event."""
        event = TelemetryEvent(
            event_type=EventType.TOOL_EXECUTION,
            customer_uuid="test-uuid",
            session_id="test-session",
            timestamp=time.time(),
            version="1.0.0",
            platform="linux",
            tool_name="test_tool",
            success=True,
            duration_ms=100.0,
        )

        assert event.event_type == EventType.TOOL_EXECUTION
        assert event.tool_name == "test_tool"
        assert event.success is True
        assert event.duration_ms == 100.0


class TestTelemetryCollector:
    """Tests for TelemetryCollector class."""

    @pytest.fixture
    def mock_config(self):
        """Mock telemetry config."""
        from blender_mcp.config import TelemetryConfig
        return TelemetryConfig(enabled=False)

    @pytest.fixture
    def collector(self, mock_config):
        """Create a TelemetryCollector with mocked config."""
        with patch('blender_mcp.config.telemetry_config', mock_config):
            with patch('blender_mcp.telemetry.HAS_SUPABASE', False):
                return TelemetryCollector()

    def test_init_disabled(self, collector):
        """Test initialization with telemetry disabled."""
        assert collector.config.enabled is False

    def test_record_event_when_disabled(self, collector):
        """Test recording event when telemetry is disabled."""
        # Should not raise exception
        collector.record_event(
            event_type=EventType.TOOL_EXECUTION,
            tool_name="test_tool",
            success=True,
            duration_ms=100.0,
        )
        # Event should be dropped silently

    @pytest.mark.parametrize("env_var", [
        "DISABLE_TELEMETRY",
        "BLENDER_MCP_DISABLE_TELEMETRY",
        "MCP_DISABLE_TELEMETRY",
    ])
    def test_disabled_via_env(self, env_var, monkeypatch):
        """Test telemetry disabled via environment variables."""
        monkeypatch.setenv(env_var, "true")

        with patch('blender_mcp.telemetry.HAS_SUPABASE', False):
            collector = TelemetryCollector()

        assert collector.config.enabled is False


class TestTelemetryFunctions:
    """Tests for telemetry utility functions."""

    def test_get_telemetry_singleton(self, reset_telemetry):
        """Test that get_telemetry returns singleton instance."""
        with patch('blender_mcp.telemetry.HAS_SUPABASE', False):
            collector1 = get_telemetry()
            collector2 = get_telemetry()

        assert collector1 is collector2

    def test_record_tool_usage(self, reset_telemetry):
        """Test record_tool_usage function."""
        with patch('blender_mcp.telemetry.HAS_SUPABASE', False):
            # Should not raise exception
            record_tool_usage("test_tool", success=True, duration_ms=100.0)

    def test_record_startup(self, reset_telemetry):
        """Test record_startup function."""
        with patch('blender_mcp.telemetry.HAS_SUPABASE', False):
            # Should not raise exception
            record_startup(blender_version="3.0.0")

    def test_is_telemetry_enabled(self, reset_telemetry):
        """Test is_telemetry_enabled function."""
        with patch('blender_mcp.telemetry.HAS_SUPABASE', False):
            result = is_telemetry_enabled()
            # Should return bool
            assert isinstance(result, bool)
