"""Tests for market data service."""
import pytest
from app.finance.market_data import MarketDataService


@pytest.mark.asyncio
async def test_get_stock_price():
    """Test fetching stock price."""
    service = MarketDataService()
    result = await service.get_stock_price("AAPL")
    
    assert result is not None
    assert "available" in result
    assert "current_price" in result or not result["available"]


@pytest.mark.asyncio
async def test_get_stock_history():
    """Test fetching stock history."""
    service = MarketDataService()
    result = await service.get_stock_history("AAPL", period="1mo")
    
    assert result is not None
    assert "available" in result
    if result["available"]:
        assert "history" in result or "prices" in result


@pytest.mark.asyncio
async def test_get_market_movers():
    """Test fetching market movers."""
    service = MarketDataService()
    result = await service.get_market_movers(market="US", limit=5)
    
    assert result is not None
    assert "gainers" in result
    assert "losers" in result


@pytest.mark.asyncio
async def test_get_sector_performance():
    """Test fetching sector performance."""
    service = MarketDataService()
    result = await service.get_sector_performance(market="US")
    
    assert result is not None
    assert "sectors" in result


@pytest.mark.asyncio
async def test_get_market_overview():
    """Test fetching market overview."""
    service = MarketDataService()
    result = await service.get_market_overview("^GSPC")
    
    assert result is not None
    assert "available" in result
