"""Financial news service for fetching and analyzing market news."""
import yfinance as yf
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class NewsService:
    """Service for fetching financial news and market updates."""
    
    def __init__(self):
        self.cache = {}
    
    async def get_market_news(self, topic: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get general market news."""
        try:
            # Using major indices to get market news
            indices = ["^GSPC", "^DJI", "^IXIC"]
            all_news = []
            
            for index in indices:
                try:
                    ticker = yf.Ticker(index)
                    news = ticker.news
                    if news:
                        for item in news[:limit]:
                            all_news.append({
                                "title": item.get('title'),
                                "link": item.get('link'),
                                "published": datetime.fromtimestamp(item.get('providerPublishTime', 0)).isoformat() if item.get('providerPublishTime') else None,
                                "source": item.get('publisher'),
                                "summary": item.get('summary'),
                                "related_symbols": [index]
                            })
                except Exception:
                    continue
            
            # Remove duplicates and sort by date
            seen = set()
            unique_news = []
            for item in all_news:
                if item['link'] not in seen:
                    seen.add(item['link'])
                    unique_news.append(item)
            
            # Sort by published date (most recent first)
            unique_news.sort(key=lambda x: x.get('published', ''), reverse=True)
            
            return unique_news[:limit]
        except Exception as e:
            return []
    
    async def get_company_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news for a specific company."""
        try:
            ticker = yf.Ticker(symbol.upper())
            news = ticker.news
            
            if not news:
                return []
            
            news_items = []
            for item in news[:limit]:
                news_items.append({
                    "title": item.get('title'),
                    "link": item.get('link'),
                    "published": datetime.fromtimestamp(item.get('providerPublishTime', 0)).isoformat() if item.get('providerPublishTime') else None,
                    "source": item.get('publisher'),
                    "summary": item.get('summary'),
                    "related_symbols": [symbol.upper()]
                })
            
            return news_items
        except Exception as e:
            return []
    
    async def get_sector_news(self, sector: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news for a specific sector."""
        # Map sectors to representative ETFs
        sector_etfs = {
            "technology": "XLK",
            "tech": "XLK",
            "healthcare": "XLV",
            "health": "XLV",
            "financials": "XLF",
            "financial": "XLF",
            "energy": "XLE",
            "consumer": "XLY",
            "utilities": "XLU"
        }
        
        etf_symbol = sector_etfs.get(sector.lower())
        if not etf_symbol:
            return []
        
        return await self.get_company_news(etf_symbol, limit)
    
    async def analyze_news_sentiment(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of news items (simplified)."""
        if not news_items:
            return {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "sentiment": "neutral"
            }
        
        # Simplified sentiment analysis based on keywords
        positive_keywords = ["growth", "rise", "gain", "profit", "beat", "strong", "up", "increase", "surge"]
        negative_keywords = ["fall", "drop", "loss", "decline", "weak", "down", "decrease", "plunge", "miss"]
        
        positive_count = 0
        negative_count = 0
        
        for item in news_items:
            title = item.get('title', '').lower()
            summary = item.get('summary', '').lower()
            text = title + ' ' + summary
            
            positive_score = sum(1 for word in positive_keywords if word in text)
            negative_score = sum(1 for word in negative_keywords if word in text)
            
            if positive_score > negative_score:
                positive_count += 1
            elif negative_score > positive_score:
                negative_count += 1
        
        neutral_count = len(news_items) - positive_count - negative_count
        
        if positive_count > negative_count:
            overall_sentiment = "positive"
        elif negative_count > positive_count:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        return {
            "total": len(news_items),
            "positive": positive_count,
            "negative": negative_count,
            "neutral": neutral_count,
            "sentiment": overall_sentiment
        }
    
    async def get_major_market_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get major market events from recent days."""
        # This is a simplified implementation
        # In production, you'd use a proper financial calendar API
        today = datetime.now()
        events = []
        
        # Example events (in production, fetch from real calendar)
        sample_events = [
            {
                "date": (today - timedelta(days=1)).isoformat(),
                "title": "Fed Interest Rate Decision",
                "impact": "high",
                "description": "Federal Reserve announced interest rate decision"
            },
            {
                "date": (today - timedelta(days=3)).isoformat(),
                "title": "Employment Data Release",
                "impact": "high",
                "description": "Monthly non-farm payroll data released"
            }
        ]
        
        return sample_events
    
    async def get_earnings_calendar(self, symbol: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming earnings announcements."""
        # Simplified implementation
        # In production, use a proper earnings calendar API
        today = datetime.now()
        
        # Sample earnings data (in production, fetch from real calendar)
        sample_earnings = [
            {
                "symbol": "AAPL",
                "company": "Apple Inc.",
                "date": (today + timedelta(days=2)).isoformat(),
                "estimated_eps": "1.52",
                "previous_eps": "1.46"
            },
            {
                "symbol": "MSFT",
                "company": "Microsoft Corporation",
                "date": (today + timedelta(days=5)).isoformat(),
                "estimated_eps": "2.82",
                "previous_eps": "2.69"
            },
            {
                "symbol": "TCS.NS",
                "company": "Tata Consultancy Services",
                "date": (today + timedelta(days=3)).isoformat(),
                "estimated_eps": "28.50",
                "previous_eps": "26.80"
            }
        ]
        
        if symbol:
            return [e for e in sample_earnings if e['symbol'].upper() == symbol.upper()]
        
        return sample_earnings
    
    async def summarize_market_news(self, limit: int = 20) -> Dict[str, Any]:
        """Get a summary of market news with sentiment analysis."""
        news_items = await self.get_market_news(limit=limit)
        sentiment = await self.analyze_news_sentiment(news_items)
        
        # Group news by themes (simplified)
        themes = {}
        for item in news_items:
            title = item.get('title', '')
            # Simple theme extraction (in production, use NLP)
            if 'earnings' in title.lower():
                theme = 'Earnings'
            elif 'fed' in title.lower() or 'rate' in title.lower():
                theme = 'Monetary Policy'
            elif 'inflation' in title.lower():
                theme = 'Inflation'
            elif 'tech' in title.lower() or 'technology' in title.lower():
                theme = 'Technology'
            else:
                theme = 'General'
            
            if theme not in themes:
                themes[theme] = []
            themes[theme].append(item)
        
        return {
            "total_news": len(news_items),
            "sentiment": sentiment,
            "themes": {k: len(v) for k, v in themes.items()},
            "top_stories": news_items[:5],
            "timestamp": datetime.now().isoformat()
        }
