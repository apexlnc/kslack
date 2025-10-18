"""Tests for agent routing logic."""

from unittest.mock import AsyncMock, Mock

import pytest


class TestAgentRouter:
    """Test cases for agent routing logic."""

    @pytest.mark.asyncio
    async def test_route_with_keyword_match(self):
        """Test routing with keyword match."""
        from kslack.services.agent_router import AgentRouter

        # Setup mock discovery
        mock_discovery = Mock()
        mock_agent = Mock()
        mock_agent.ready = True
        mock_agent.extract_keywords = Mock(return_value=["kubernetes", "k8s", "pods"])

        mock_discovery.discover_agents = AsyncMock(
            return_value={"kagent/k8s-agent": mock_agent}
        )

        router = AgentRouter(mock_discovery)

        # Route message with keyword
        namespace, name, reason = await router.route("show me failing pods", "user123")

        assert namespace == "kagent"
        assert name == "k8s-agent"
        assert "keyword" in reason.lower()

    @pytest.mark.asyncio
    async def test_route_with_no_keyword_match_uses_default(self):
        """Test routing falls back to default when no keyword matches."""
        from kslack.services.agent_router import AgentRouter

        # Setup mock discovery
        mock_discovery = Mock()
        mock_agent = Mock()
        mock_agent.ready = True
        mock_agent.extract_keywords = Mock(return_value=["kubernetes", "k8s", "pods"])

        mock_discovery.discover_agents = AsyncMock(
            return_value={"kagent/k8s-agent": mock_agent}
        )

        router = AgentRouter(mock_discovery)

        # Route message with no matching keywords
        namespace, name, reason = await router.route("hello world", "user123")

        assert namespace == "kagent"
        assert name == "k8s-agent"
        assert "default" in reason.lower()

    @pytest.mark.asyncio
    async def test_route_with_case_insensitive_matching(self):
        """Test keyword matching is case-insensitive."""
        from kslack.services.agent_router import AgentRouter

        # Setup mock discovery
        mock_discovery = Mock()
        mock_agent = Mock()
        mock_agent.ready = True
        mock_agent.extract_keywords = Mock(return_value=["kubernetes", "k8s"])

        mock_discovery.discover_agents = AsyncMock(
            return_value={"kagent/k8s-agent": mock_agent}
        )

        router = AgentRouter(mock_discovery)

        # Route with uppercase keyword
        namespace, name, reason = await router.route("Show me KUBERNETES pods", "user123")

        assert namespace == "kagent"
        assert name == "k8s-agent"
        assert "keyword" in reason.lower()

    @pytest.mark.asyncio
    async def test_user_explicit_agent(self):
        """Test user-specific agent override."""
        from kslack.services.agent_router import AgentRouter

        mock_discovery = Mock()
        router = AgentRouter(mock_discovery)

        # Set user explicit agent
        router.set_explicit_agent("user123", "kagent", "security-agent")

        # Route should use explicit selection regardless of keywords
        namespace, name, reason = await router.route("hello", "user123")

        assert namespace == "kagent"
        assert name == "security-agent"
        assert "explicit" in reason.lower()

    @pytest.mark.asyncio
    async def test_clear_explicit_agent(self):
        """Test clearing user-specific override."""
        from kslack.services.agent_router import AgentRouter

        # Setup mock discovery
        mock_discovery = Mock()
        mock_agent = Mock()
        mock_agent.ready = True
        mock_agent.extract_keywords = Mock(return_value=["pods"])

        mock_discovery.discover_agents = AsyncMock(
            return_value={"kagent/k8s-agent": mock_agent}
        )

        router = AgentRouter(mock_discovery)

        # Set and then clear explicit agent
        router.set_explicit_agent("user123", "kagent", "security-agent")
        router.clear_explicit_agent("user123")

        # Should use keyword routing again
        namespace, name, reason = await router.route("show pods", "user123")

        assert namespace == "kagent"
        assert name == "k8s-agent"
        assert "keyword" in reason.lower()
