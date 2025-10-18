"""Tests for configuration loading and validation."""

import os
from unittest.mock import patch

import pytest

from kslack.config import load_config


class TestConfigValidation:
    """Test cases for configuration validation."""

    def test_missing_required_env_vars(self):
        """Test that missing required variables raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables"):
                load_config()

    def test_invalid_bot_token_prefix(self):
        """Test that bot token must start with xoxb-."""
        with patch.dict(
            os.environ,
            {
                "SLACK_BOT_TOKEN": "invalid-token",
                "SLACK_APP_TOKEN": "xapp-test-token-12345678901234567890",
                "SLACK_SIGNING_SECRET": "test-secret",
                "KAGENT_BASE_URL": "http://localhost:8083",
            },
        ):
            with pytest.raises(ValueError, match="SLACK_BOT_TOKEN must start with 'xoxb-'"):
                load_config()

    def test_invalid_app_token_prefix(self):
        """Test that app token must start with xapp-."""
        with patch.dict(
            os.environ,
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token-12345678901234567890",
                "SLACK_APP_TOKEN": "invalid-token",
                "SLACK_SIGNING_SECRET": "test-secret",
                "KAGENT_BASE_URL": "http://localhost:8083",
            },
        ):
            with pytest.raises(ValueError, match="SLACK_APP_TOKEN must start with 'xapp-'"):
                load_config()

    def test_invalid_url_no_scheme(self):
        """Test that URL must include a scheme."""
        with patch.dict(
            os.environ,
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token-12345678901234567890",
                "SLACK_APP_TOKEN": "xapp-test-token-12345678901234567890",
                "SLACK_SIGNING_SECRET": "test-secret",
                "KAGENT_BASE_URL": "localhost:8083",
            },
        ):
            # urlparse treats "localhost:8083" as having scheme="localhost" and no netloc
            # So it fails on the netloc check, not the scheme check
            with pytest.raises(ValueError, match="KAGENT_BASE_URL must include a hostname"):
                load_config()

    def test_invalid_port_range(self):
        """Test that port must be in valid range."""
        with patch.dict(
            os.environ,
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token-12345678901234567890",
                "SLACK_APP_TOKEN": "xapp-test-token-12345678901234567890",
                "SLACK_SIGNING_SECRET": "test-secret",
                "KAGENT_BASE_URL": "http://localhost:8083",
                "SERVER_PORT": "99999",
            },
        ):
            with pytest.raises(ValueError, match="SERVER_PORT must be between 1 and 65535"):
                load_config()

    def test_invalid_log_level(self):
        """Test that log level must be valid."""
        with patch.dict(
            os.environ,
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token-12345678901234567890",
                "SLACK_APP_TOKEN": "xapp-test-token-12345678901234567890",
                "SLACK_SIGNING_SECRET": "test-secret",
                "KAGENT_BASE_URL": "http://localhost:8083",
                "LOG_LEVEL": "INVALID",
            },
        ):
            with pytest.raises(ValueError, match="LOG_LEVEL must be one of"):
                load_config()

    def test_valid_config(self):
        """Test that valid configuration loads successfully."""
        with patch.dict(
            os.environ,
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token-12345678901234567890",
                "SLACK_APP_TOKEN": "xapp-test-token-12345678901234567890",
                "SLACK_SIGNING_SECRET": "test-secret",
                "KAGENT_BASE_URL": "http://localhost:8083",
            },
        ):
            config = load_config()
            assert config.slack.bot_token.startswith("xoxb-")
            assert config.slack.app_token.startswith("xapp-")
            assert config.kagent.base_url == "http://localhost:8083"
            assert config.server.port == 8080
            assert config.log_level == "INFO"

    def test_config_with_optional_values(self):
        """Test configuration with optional values set."""
        with patch.dict(
            os.environ,
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token-12345678901234567890",
                "SLACK_APP_TOKEN": "xapp-test-token-12345678901234567890",
                "SLACK_SIGNING_SECRET": "test-secret",
                "KAGENT_BASE_URL": "https://kagent.example.com",
                "KAGENT_TIMEOUT": "60",
                "SERVER_HOST": "127.0.0.1",
                "SERVER_PORT": "9090",
                "LOG_LEVEL": "DEBUG",
                "PERMISSIONS_FILE": "custom/permissions.yaml",
            },
        ):
            config = load_config()
            assert config.kagent.base_url == "https://kagent.example.com"
            assert config.kagent.timeout == 60
            assert config.server.host == "127.0.0.1"
            assert config.server.port == 9090
            assert config.log_level == "DEBUG"
            assert config.permissions_file == "custom/permissions.yaml"
