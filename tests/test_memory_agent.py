"""Tests for memory agent."""
import pytest
from unittest.mock import Mock, AsyncMock
from app.ai.agents.memory_agent import MemoryAgent


@pytest.fixture
def mock_ai_provider():
    """Mock AI provider."""
    provider = Mock()
    provider.generate_response = AsyncMock(return_value="Test response")
    return provider


@pytest.fixture
def memory_agent(mock_ai_provider):
    """Create memory agent instance."""
    return MemoryAgent(mock_ai_provider)


def test_update_user_memory(memory_agent):
    """Test updating user memory."""
    memory_agent.update_user_memory(1, "test_key", "test_value")
    
    result = memory_agent.get_user_memory(1, "test_key")
    
    assert result == "test_value"


def test_get_user_memory(memory_agent):
    """Test getting user memory."""
    memory_agent.update_user_memory(1, "symbols", ["AAPL", "MSFT"])
    
    result = memory_agent.get_user_memory(1)
    
    assert result is not None
    assert "symbols" in result


def test_track_conversation_context(memory_agent):
    """Test tracking conversation context."""
    memory_agent.track_conversation_context(
        user_id=1,
        last_intent="stock_lookup",
        last_symbol="AAPL",
        last_topic="technology"
    )
    
    result = memory_agent.get_conversation_context(1)
    
    assert result["last_intent"] == "stock_lookup"
    assert result["last_symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_learn_from_interaction(memory_agent, mock_ai_provider):
    """Test learning from interaction."""
    await memory_agent.learn_from_interaction(
        user_id=1,
        user_message="I'm interested in AAPL",
        intent="stock_lookup",
        entities={"symbols": ["AAPL"]}
    )
    
    result = memory_agent.get_user_memory(1, "mentioned_symbols")
    
    assert "AAPL" in result


@pytest.mark.asyncio
async def test_get_personalized_context(memory_agent):
    """Test getting personalized context."""
    memory_agent.update_user_memory(1, "mentioned_symbols", ["AAPL", "MSFT"])
    memory_agent.track_conversation_context(1, "stock_lookup", "AAPL")
    
    result = await memory_agent.get_personalized_context(1)
    
    assert result["user_id"] == 1
    assert len(result["readable_context"]) > 0


@pytest.mark.asyncio
async def test_suggest_follow_up_questions(memory_agent):
    """Test suggesting follow-up questions."""
    memory_agent.track_conversation_context(1, "company_research", "AAPL")
    
    result = await memory_agent.suggest_follow_up_questions(1, "company_research", "AAPL")
    
    assert isinstance(result, list)
    assert len(result) > 0
