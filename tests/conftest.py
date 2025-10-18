"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def mock_slack_config():
    """Mock Slack configuration for tests."""
    from kslack.config import SlackConfig

    return SlackConfig(
        bot_token="xoxb-test-token-12345678901234567890",
        app_token="xapp-test-token-12345678901234567890",
        signing_secret="test-signing-secret-1234567890abcdef",
    )


@pytest.fixture
def mock_kagent_config():
    """Mock Kagent configuration for tests."""
    from kslack.config import KagentConfig

    return KagentConfig(
        base_url="http://localhost:8083",
        timeout=30,
    )


@pytest.fixture
def mock_config(mock_slack_config, mock_kagent_config):
    """Mock complete configuration for tests."""
    from kslack.config import Config, ServerConfig

    return Config(
        slack=mock_slack_config,
        kagent=mock_kagent_config,
        server=ServerConfig(host="0.0.0.0", port=8080),
        permissions_file="config/permissions.yaml",
        log_level="INFO",
    )
