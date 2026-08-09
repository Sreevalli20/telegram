"""Tests for watchlist service."""
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.watchlist_service import WatchlistService


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = Mock()
    return db


@pytest.fixture
def watchlist_service(mock_db):
    """Create watchlist service instance."""
    return WatchlistService(mock_db)


@pytest.mark.asyncio
async def test_add_to_watchlist(watchlist_service, mock_db):
    """Test adding stock to watchlist."""
    # Mock repository methods
    watchlist_service.watchlist_repo.add_to_watchlist = Mock(return_value=Mock(symbol="AAPL"))
    watchlist_service.company_data.get_company_overview = AsyncMock(return_value={"company_name": "Apple Inc."})
    
    result = await watchlist_service.add_to_watchlist(1, "AAPL")
    
    assert result["success"] is True
    assert result["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_remove_from_watchlist(watchlist_service, mock_db):
    """Test removing stock from watchlist."""
    watchlist_service.watchlist_repo.remove_from_watchlist = Mock(return_value=True)
    
    result = watchlist_service.remove_from_watchlist(1, "AAPL")
    
    assert result["success"] is True
    assert result["symbol"] == "AAPL"


def test_get_watchlist(watchlist_service, mock_db):
    """Test getting watchlist."""
    watchlist_service.watchlist_repo.get_user_watchlist = Mock(return_value=[
        Mock(symbol="AAPL", company_name="Apple Inc.", notes=None, alert_price_above=None, alert_price_below=None, created_at=Mock(isoformat=Mock(return_value="2024-01-01")))
    ])
    
    result = watchlist_service.get_watchlist(1)
    
    assert len(result) == 1
    assert result[0]["symbol"] == "AAPL"


def test_set_price_alert(watchlist_service, mock_db):
    """Test setting price alerts."""
    watchlist_service.watchlist_repo.get_by_symbol = Mock(return_value=None)
    watchlist_service.watchlist_repo.add_to_watchlist = Mock(return_value=Mock())
    watchlist_service.watchlist_repo.set_price_alert = Mock(return_value=Mock())
    
    result = watchlist_service.set_price_alert(1, "AAPL", alert_above=200)
    
    assert result["success"] is True
    assert result["alert_above"] == 200
