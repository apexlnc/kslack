"""Tests for Slack message validation and sanitization."""

import pytest


class TestSlackValidators:
    """Test cases for Slack validation utilities."""

    def test_strip_bot_mention_with_user_id(self):
        """Test stripping @bot mention with user ID."""
        from kslack.slack.validators import strip_bot_mention

        text = "<@U01ABC123> hello world"
        result = strip_bot_mention(text)
        assert result == "hello world"

    def test_strip_bot_mention_multiple_spaces(self):
        """Test stripping mention removes mention but preserves spacing."""
        from kslack.slack.validators import strip_bot_mention

        text = "<@U01ABC123>   hello   world"
        result = strip_bot_mention(text)
        # strip() is called at the end, so extra spaces are trimmed
        assert result == "hello   world"

    def test_strip_bot_mention_no_mention(self):
        """Test text without mention is unchanged."""
        from kslack.slack.validators import strip_bot_mention

        text = "hello world"
        result = strip_bot_mention(text)
        assert result == "hello world"

    def test_sanitize_message_removes_extra_whitespace(self):
        """Test sanitizing removes extra whitespace."""
        from kslack.slack.validators import sanitize_message

        text = "  hello   world  "
        result = sanitize_message(text)
        # regex replaces multiple spaces with single space
        assert result == "hello world"

    def test_sanitize_message_handles_newlines(self):
        """Test sanitizing converts newlines to spaces."""
        from kslack.slack.validators import sanitize_message

        text = "hello\n\n\nworld"
        result = sanitize_message(text)
        # \s+ regex includes newlines
        assert "hello" in result
        assert "world" in result
        assert result == "hello world"

    def test_validate_message_accepts_valid_text(self):
        """Test validation accepts valid messages."""
        from kslack.slack.validators import validate_message

        assert validate_message("hello") is True
        assert validate_message("hello world") is True

    def test_validate_message_rejects_empty(self):
        """Test validation rejects empty messages."""
        from kslack.slack.validators import validate_message

        assert validate_message("") is False
        assert validate_message("   ") is False

    def test_validate_message_handles_none(self):
        """Test validation handles None input."""
        from kslack.slack.validators import validate_message

        # validate_message returns False for None
        result = validate_message(None)
        assert result is False

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("hello", True),
            ("hello world", True),
            ("  hello  ", True),  # Stripped to "hello", passes
            ("", False),
            ("   ", False),  # Stripped to "", fails MIN_MESSAGE_LENGTH
        ],
    )
    def test_validate_message_parametrized(self, text, expected):
        """Test message validation with various inputs."""
        from kslack.slack.validators import validate_message

        assert validate_message(text) == expected
