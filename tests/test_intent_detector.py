"""Tests for intent detector."""
import pytest
from app.ai.intent_detector import IntentDetector


def test_detect_stock_lookup_intent():
    """Test detecting stock lookup intent."""
    detector = IntentDetector()
    result = detector.detect_intent("What is the price of AAPL?")
    
    assert result is not None
    assert result["intent"] == "stock_lookup"
    assert "AAPL" in result["entities"]["symbols"]


def test_detect_market_analysis_intent():
    """Test detecting market analysis intent."""
    detector = IntentDetector()
    result = detector.detect_intent("How is the market doing today?")
    
    assert result is not None
    assert result["intent"] == "market_analysis"


def test_detect_company_research_intent():
    """Test detecting company research intent."""
    detector = IntentDetector()
    result = detector.detect_intent("Tell me about Microsoft's financials")
    
    assert result is not None
    assert result["intent"] == "company_research"


def test_detect_comparison_intent():
    """Test detecting comparison intent."""
    detector = IntentDetector()
    result = detector.detect_intent("Compare Apple and Google")
    
    assert result is not None
    assert result["intent"] == "comparison"


def test_detect_watchlist_intent():
    """Test detecting watchlist intent."""
    detector = IntentDetector()
    result = detector.detect_intent("Add AAPL to my watchlist")
    
    assert result is not None
    assert result["intent"] == "watchlist"


def test_extract_symbols():
    """Test symbol extraction."""
    detector = IntentDetector()
    result = detector.detect_intent("What about TSLA and MSFT?")
    
    assert result is not None
    assert "TSLA" in result["entities"]["symbols"]
    assert "MSFT" in result["entities"]["symbols"]


def test_extract_price_alerts():
    """Test price alert extraction."""
    detector = IntentDetector()
    result = detector.detect_intent("Alert me if AAPL goes above 200")
    
    assert result is not None
    assert result["entities"].get("alert_above") == 200
