import os
from dataclasses import dataclass
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


@dataclass
class SlackConfig:
    """Slack-specific configuration"""

    bot_token: str
    app_token: str
    signing_secret: str


@dataclass
class KagentConfig:
    """Kagent API configuration"""

    base_url: str
    timeout: int = 30


@dataclass
class ServerConfig:
    """HTTP server configuration"""

    host: str = "0.0.0.0"
    port: int = 8080


@dataclass
class Config:
    """Main application configuration"""

    slack: SlackConfig
    kagent: KagentConfig
    server: ServerConfig
    permissions_file: str = "config/permissions.yaml"
    log_level: str = "INFO"


def _validate_slack_token(token: str, prefix: str, name: str) -> None:
    """Validate Slack token format"""
    if not token.startswith(prefix):
        raise ValueError(f"{name} must start with '{prefix}' (got: {token[:10]}...)")
    if len(token) < 20:
        raise ValueError(f"{name} appears too short to be valid")


def _validate_url(url: str, name: str) -> None:
    """Validate URL format"""
    parsed = urlparse(url)
    if not parsed.scheme:
        raise ValueError(f"{name} must include a scheme (http:// or https://)")
    if not parsed.netloc:
        raise ValueError(f"{name} must include a hostname")
    if parsed.scheme not in ["http", "https"]:
        raise ValueError(f"{name} must use http or https scheme (got: {parsed.scheme})")


def _validate_port(port: int, name: str) -> None:
    """Validate port number"""
    if not 1 <= port <= 65535:
        raise ValueError(f"{name} must be between 1 and 65535 (got: {port})")


def _validate_log_level(level: str) -> None:
    """Validate log level"""
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if level.upper() not in valid_levels:
        raise ValueError(f"LOG_LEVEL must be one of {valid_levels} (got: {level})")


def load_config() -> Config:
    """Load configuration from environment variables"""

    # Required variables
    required = [
        "SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN",
        "SLACK_SIGNING_SECRET",
        "KAGENT_BASE_URL",
    ]

    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    # Extract values
    bot_token = os.environ["SLACK_BOT_TOKEN"]
    app_token = os.environ["SLACK_APP_TOKEN"]
    signing_secret = os.environ["SLACK_SIGNING_SECRET"]
    kagent_base_url = os.environ["KAGENT_BASE_URL"]
    kagent_timeout = int(os.getenv("KAGENT_TIMEOUT", "30"))
    server_host = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port = int(os.getenv("SERVER_PORT", "8080"))
    log_level = os.getenv("LOG_LEVEL", "INFO")

    # Validate Slack tokens
    _validate_slack_token(bot_token, "xoxb-", "SLACK_BOT_TOKEN")
    _validate_slack_token(app_token, "xapp-", "SLACK_APP_TOKEN")

    # Validate URLs
    _validate_url(kagent_base_url, "KAGENT_BASE_URL")

    # Validate port
    _validate_port(server_port, "SERVER_PORT")

    # Validate log level
    _validate_log_level(log_level)

    # Validate timeout
    if kagent_timeout < 1:
        raise ValueError(f"KAGENT_TIMEOUT must be positive (got: {kagent_timeout})")

    return Config(
        slack=SlackConfig(
            bot_token=bot_token,
            app_token=app_token,
            signing_secret=signing_secret,
        ),
        kagent=KagentConfig(
            base_url=kagent_base_url,
            timeout=kagent_timeout,
        ),
        server=ServerConfig(
            host=server_host,
            port=server_port,
        ),
        permissions_file=os.getenv("PERMISSIONS_FILE", "config/permissions.yaml"),
        log_level=log_level,
    )
