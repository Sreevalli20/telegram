"""Tests for document agent."""
import pytest
from unittest.mock import Mock, AsyncMock
from io import BytesIO
from app.ai.agents.document_agent import DocumentAgent


@pytest.fixture
def mock_ai_provider():
    """Mock AI provider."""
    provider = Mock()
    provider.generate_response = AsyncMock(return_value="Test analysis")
    return provider


@pytest.fixture
def document_agent(mock_ai_provider):
    """Create document agent instance."""
    return DocumentAgent(mock_ai_provider)


def test_extract_text_from_pdf(document_agent):
    """Test PDF text extraction."""
    # This is a placeholder test - actual PDF testing would require sample PDFs
    pdf_content = b"%PDF-1.4\n%fake pdf content"
    pdf_file = BytesIO(pdf_content)
    
    result = document_agent.extract_text_from_pdf(pdf_file)
    
    # Since we don't have a real PDF, we expect an error or empty result
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_analyze_financial_document(document_agent, mock_ai_provider):
    """Test document analysis."""
    document_text = "Revenue: $100M, Profit: $20M"
    
    result = await document_agent.analyze_financial_document(
        document_text,
        document_type="earnings_report",
        document_id="test_doc_1"
    )
    
    assert result["available"] is True
    assert result["document_type"] == "earnings_report"
    assert "analysis" in result


@pytest.mark.asyncio
async def test_extract_financial_data(document_agent, mock_ai_provider):
    """Test financial data extraction."""
    document_text = "Revenue: $100M, Net Income: $20M, EPS: $2.50"
    
    result = await document_agent.extract_financial_data(document_text)
    
    assert result["available"] is True
    assert "extracted_data" in result


@pytest.mark.asyncio
async def test_summarize_document(document_agent, mock_ai_provider):
    """Test document summarization."""
    document_text = "Long financial report text..."
    
    result = await document_agent.summarize_document(document_text, max_length=100)
    
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_chat_about_document(document_agent, mock_ai_provider):
    """Test document chat."""
    # First, add a document to context
    document_agent.document_context["test_doc"] = {
        "text": "Test document content",
        "type": "report",
        "analysis": "Test analysis"
    }
    
    result = await document_agent.chat_about_document(
        "What is the revenue?",
        "test_doc"
    )
    
    assert isinstance(result, str)


def test_clear_document_context(document_agent):
    """Test clearing document context."""
    document_agent.document_context["test_doc"] = {"text": "test"}
    document_agent.clear_document_context("test_doc")
    
    assert "test_doc" not in document_agent.document_context


def test_get_document_context(document_agent):
    """Test getting document context."""
    document_agent.document_context["test_doc"] = {"text": "test"}
    
    result = document_agent.get_document_context("test_doc")
    
    assert result is not None
    assert result["text"] == "test"
