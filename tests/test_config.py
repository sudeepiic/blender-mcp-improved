"""
Tests for the config module.
"""

import pytest
import os

from blender_mcp.config import TelemetryConfig, telemetry_config


class TestTelemetryConfig:
    """Tests for TelemetryConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = TelemetryConfig()

        assert config.enabled is True
        assert config.supabase_url == ""
        assert config.supabase_anon_key == ""
        assert config.max_prompt_length == 500

    def test_custom_values(self):
        """Test configuration with custom values."""
        config = TelemetryConfig(
            enabled=False,
            supabase_url="https://test.supabase.co",
            supabase_anon_key="test-key",
            max_prompt_length=1000,
        )

        assert config.enabled is False
        assert config.supabase_url == "https://test.supabase.co"
        assert config.supabase_anon_key == "test-key"
        assert config.max_prompt_length == 1000

    def test_env_override_enabled(self, monkeypatch):
        """Test disabling via environment variable."""
        monkeypatch.setenv("BLENDER_MCP_TELEMETRY_ENABLED", "false")

        config = TelemetryConfig()
        assert config.enabled is False

    @pytest.mark.parametrize("env_value", ["false", "0", "no", "off", "FALSE", "No"])
    def test_env_override_values(self, env_value, monkeypatch):
        """Test various environment values that disable telemetry."""
        monkeypatch.setenv("BLENDER_MCP_TELEMETRY_ENABLED", env_value)

        config = TelemetryConfig()
        assert config.enabled is False

    def test_env_override_supabase(self, monkeypatch):
        """Test Supabase credentials via environment variables."""
        monkeypatch.setenv("BLENDER_MCP_SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("BLENDER_MCP_SUPABASE_ANON_KEY", "test-key-123")

        config = TelemetryConfig()

        assert config.supabase_url == "https://test.supabase.co"
        assert config.supabase_anon_key == "test-key-123"


class TestGlobalConfig:
    """Tests for global telemetry_config instance."""

    def test_global_config_exists(self):
        """Test that global config is accessible."""
        assert hasattr(telemetry_config, 'enabled')
        assert hasattr(telemetry_config, 'supabase_url')
        assert hasattr(telemetry_config, 'supabase_anon_key')
        assert hasattr(telemetry_config, 'max_prompt_length')

    def test_global_config_types(self):
        """Test that global config has correct types."""
        assert isinstance(telemetry_config.enabled, bool)
        assert isinstance(telemetry_config.max_prompt_length, int)
