"""Market data service for fetching real-time financial market information with caching and error handling."""
import yfinance as yf
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import time
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MarketDataService:
    """Service for fetching market data from financial APIs with caching and retry logic."""
    
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 300  # 5 minutes cache
        self.max_retries = 3
        self.base_retry_delay = 2  # seconds
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache:
            return False
        if key not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[key]
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if valid."""
        if self._is_cache_valid(key):
            logger.debug(f"Cache hit for key: {key}")
            return self.cache[key]
        return None
    
    def _set_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Set data in cache with expiry."""
        self.cache[key] = data
        self.cache_expiry[key] = datetime.now() + timedelta(seconds=self.cache_duration)
        logger.debug(f"Cached data for key: {key}")
    
    async def _retry_with_backoff(self, func, *args, **kwargs) -> Any:
        """Execute function with exponential backoff retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                # Don't retry on certain errors
                if "404" in error_msg or "not found" in error_msg:
                    logger.error(f"Non-retryable error: {e}")
                    raise
                
                # Check for rate limiting - DO NOT retry aggressively on 429
                if "429" in error_msg or "too many requests" in error_msg:
                    logger.warning(f"Rate limited (429) - stopping retries to avoid further blocking")
                    # For 429, we raise immediately and let the caller handle it gracefully
                    raise
                else:
                    # For other errors, shorter wait
                    wait_time = self.base_retry_delay
                    logger.warning(f"Error on attempt {attempt + 1}/{self.max_retries}: {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
        
        # All retries exhausted
        logger.error(f"All {self.max_retries} retry attempts failed. Last error: {last_error}")
        raise last_error
    
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get current stock price and basic data with caching and retry logic."""
        cache_key = f"stock_price_{symbol.upper()}"
        
        # Try cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Fetch fresh data with retry logic
        async def fetch_stock_data():
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            previous_close = info.get('previousClose')
            
            change = None
            change_percent = None
            if current_price and previous_close:
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close != 0 else None
            
            return {
                "symbol": symbol.upper(),
                "current_price": current_price,
                "previous_close": previous_close,
                "change": change,
                "change_percent": change_percent,
                "volume": info.get('volume'),
                "market_cap": info.get('marketCap'),
                "currency": info.get('currency'),
                "last_updated": datetime.now().isoformat(),
                "available": True
            }
        
        try:
            data = await self._retry_with_backoff(fetch_stock_data)
            self._set_cache(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"Failed to fetch stock price for {symbol}: {str(e)}")
            return {
                "symbol": symbol.upper(),
                "error": str(e),
                "available": False
            }
    
    async def get_stock_history(
        self, 
        symbol: str, 
        period: str = "1mo",
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """Get historical stock data."""
        try:
            ticker = yf.Ticker(symbol.upper())
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return {
                    "symbol": symbol.upper(),
                    "data": [],
                    "available": False
                }
            
            data = []
            for date, row in hist.iterrows():
                data.append({
                    "date": date.isoformat(),
                    "open": float(row['Open']) if 'Open' in row else None,
                    "high": float(row['High']) if 'High' in row else None,
                    "low": float(row['Low']) if 'Low' in row else None,
                    "close": float(row['Close']) if 'Close' in row else None,
                    "volume": int(row['Volume']) if 'Volume' in row else None
                })
            
            return {
                "symbol": symbol.upper(),
                "period": period,
                "interval": interval,
                "data": data,
                "available": True
            }
        except Exception as e:
            return {
                "symbol": symbol.upper(),
                "error": str(e),
                "available": False
            }
    
    async def get_index_data(self, index: str) -> Dict[str, Any]:
        """Get market index data (e.g., ^NSEI, ^GSPC, ^DJI)."""
        return await self.get_stock_price(index)
    
    async def get_market_movers(
        self, 
        market: str = "US",
        limit: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get top market movers (gainers and losers)."""
        # This is a simplified implementation
        # In production, you'd use a proper financial API
        try:
            # Common indices and stocks to track
            symbols = {
                "US": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "WMT"],
                "INDIA": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS"]
            }
            
            selected_symbols = symbols.get(market.upper(), symbols["US"])
            
            # Fetch data for all symbols
            tasks = [self.get_stock_price(symbol) for symbol in selected_symbols]
            results = await asyncio.gather(*tasks)
            
            # Filter valid results and sort by change percent
            valid_results = [r for r in results if r.get("available", False) and r.get("change_percent") is not None]
            
            gainers = sorted(valid_results, key=lambda x: x["change_percent"], reverse=True)[:limit]
            losers = sorted(valid_results, key=lambda x: x["change_percent"])[:limit]
            
            return {
                "gainers": gainers,
                "losers": losers,
                "market": market,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "gainers": [],
                "losers": [],
                "error": str(e)
            }
    
    async def get_sector_performance(self, market: str = "US") -> Dict[str, Any]:
        """Get sector-wise market performance."""
        # Simplified implementation - in production use sector ETFs
        sector_etfs = {
            "Technology": "XLK",
            "Healthcare": "XLV",
            "Financials": "XLF",
            "Energy": "XLE",
            "Consumer": "XLY",
            "Utilities": "XLU"
        }
        
        sectors = {}
        for sector, etf in sector_etfs.items():
            data = await self.get_stock_price(etf)
            if data.get("available"):
                sectors[sector] = {
                    "change_percent": data.get("change_percent"),
                    "current_price": data.get("current_price")
                }
        
        return {
            "sectors": sectors,
            "market": market,
            "timestamp": datetime.now().isoformat()
        }
    
    async def search_symbols(self, query: str) -> List[Dict[str, str]]:
        """Search for stock symbols by company name or symbol."""
        # This is a simplified implementation
        # In production, use a proper symbol search API
        common_stocks = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "google": "GOOGL",
            "alphabet": "GOOGL",
            "amazon": "AMZN",
            "tesla": "TSLA",
            "meta": "META",
            "facebook": "META",
            "nvidia": "NVDA",
            "reliance": "RELIANCE.NS",
            "tcs": "TCS.NS",
            "hdfc": "HDFCBANK.NS",
            "infosys": "INFY.NS",
            "icici": "ICICIBANK.NS",
            "sbi": "SBIN.NS"
        }
        
        query_lower = query.lower()
        matches = []
        
        for name, symbol in common_stocks.items():
            if query_lower in name or query_lower in symbol.lower():
                matches.append({
                    "symbol": symbol,
                    "name": name.capitalize()
                })
        
        return matches[:5]  # Return top 5 matches
