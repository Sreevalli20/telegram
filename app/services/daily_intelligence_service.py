"""Daily intelligence service for generating market briefings."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.repositories.watchlist_repository import WatchlistRepository
from app.finance import MarketDataService, NewsService
from datetime import datetime
from app.ai.providers import BaseAIProvider


class DailyIntelligenceService:
    """Service for generating daily financial briefings."""
    
    def __init__(self, db: Session, ai_provider: BaseAIProvider):
        self.db = db
        self.ai_provider = ai_provider
        self.watchlist_repo = WatchlistRepository(db)
        self.market_data = MarketDataService()
        self.news_service = NewsService()
    
    async def generate_morning_brief(self, user_id: int) -> Dict[str, Any]:
        """Generate morning market briefing."""
        # Fetch market data
        market_movers = await self.market_data.get_market_movers(market="US", limit=5)
        sector_performance = await self.market_data.get_sector_performance(market="US")
        market_news = await self.news_service.get_market_news(limit=10)
        news_summary = await self.news_service.summarize_market_news(limit=20)
        
        # Fetch watchlist performance
        watchlist_items = self.watchlist_repo.get_user_watchlist(user_id)
        watchlist_performance = []
        
        for item in watchlist_items[:5]:  # Top 5 watchlist items
            price_data = await self.market_data.get_stock_price(item.symbol)
            if price_data.get("available"):
                watchlist_performance.append({
                    "symbol": item.symbol,
                    "company_name": item.company_name,
                    "change_percent": price_data.get("change_percent"),
                    "current_price": price_data.get("current_price")
                })
        
        # Build briefing context
        briefing_context = f"""MORNING MARKET BRIEFING - {datetime.now().strftime('%B %d, %Y')}

MARKET OVERVIEW:
Market Sentiment: {news_summary.get('sentiment', {}).get('sentiment', 'neutral')}
Total News Stories: {news_summary.get('total_news', 0)}

TOP GAINERS:
{chr(10).join([f"{g['symbol']}: +{g.get('change_percent', 0):.2f}%" for g in market_movers.get('gainers', [])[:3]])}

TOP LOSERS:
{chr(10).join([f"{l['symbol']}: {l.get('change_percent', 0):.2f}%" for l in market_movers.get('losers', [])[:3]])}

SECTOR PERFORMANCE:
{chr(10).join([f"{sector}: {data.get('change_percent', 0):.2f}%" for sector, data in sector_performance.get('sectors', {}).items()])}

YOUR WATCHLIST:
{chr(10).join([f"{w['symbol']}: {w.get('change_percent', 0):.2f}%" for w in watchlist_performance]) if watchlist_performance else 'Your watchlist is empty'}

TOP NEWS STORIES:
{chr(10).join([f"{i+1}. {news.get('title', 'N/A')}" for i, news in enumerate(market_news[:5])])}
"""
        
        system_prompt = """You are ATLAS, an AI Financial Assistant providing a morning market briefing.

Create a concise, professional morning briefing that includes:
1. **Market Summary**: Overall market sentiment and key movements
2. **Watchlist Update**: Performance of user's tracked stocks
3. **Key News**: Top 2-3 market-moving stories
4. **What to Watch**: Important events or earnings today
5. **Quick Insight**: One actionable insight for the day

Be concise (under 300 words), professional, and focus on what matters for decision-making. Use emojis sparingly for emphasis."""
        
        briefing = await self.ai_provider.generate_response(
            prompt=f"Generate morning briefing:\n{briefing_context}",
            context=system_prompt,
            temperature=0.6
        )
        
        return {
            "type": "morning_brief",
            "briefing": briefing,
            "data": {
                "market_movers": market_movers,
                "sector_performance": sector_performance,
                "watchlist_performance": watchlist_performance,
                "news_summary": news_summary
            },
            "generated_at": datetime.now().isoformat()
        }
    
    async def generate_evening_summary(self, user_id: int) -> Dict[str, Any]:
        """Generate evening market summary."""
        # Fetch market data
        market_movers = await self.market_data.get_market_movers(market="US", limit=5)
        market_news = await self.news_service.get_market_news(limit=10)
        
        # Fetch watchlist performance
        watchlist_items = self.watchlist_repo.get_user_watchlist(user_id)
        watchlist_performance = []
        
        for item in watchlist_items:
            price_data = await self.market_data.get_stock_price(item.symbol)
            if price_data.get("available"):
                watchlist_performance.append({
                    "symbol": item.symbol,
                    "company_name": item.company_name,
                    "change_percent": price_data.get("change_percent"),
                    "current_price": price_data.get("current_price")
                })
        
        # Calculate watchlist summary
        if watchlist_performance:
            gainers = [w for w in watchlist_performance if w.get("change_percent", 0) > 0]
            losers = [w for w in watchlist_performance if w.get("change_percent", 0) < 0]
            best = max(watchlist_performance, key=lambda x: x.get("change_percent", 0)) if watchlist_performance else None
            worst = min(watchlist_performance, key=lambda x: x.get("change_percent", 0)) if watchlist_performance else None
        else:
            gainers, losers, best, worst = [], [], None, None
        
        # Build summary context
        summary_context = f"""EVENING MARKET SUMMARY - {datetime.now().strftime('%B %d, %Y')}

DAY'S HIGHLIGHTS:
Top Gainers: {', '.join([f"{g['symbol']} (+{g.get('change_percent', 0):.2f}%)" for g in market_movers.get('gainers', [])[:3]])}
Top Losers: {', '.join([f"{l['symbol']} ({l.get('change_percent', 0):.2f}%)" for l in market_movers.get('losers', [])[:3]])}

YOUR WATCHLIST PERFORMANCE:
Total Items: {len(watchlist_performance)}
Gainers: {len(gainers)}
Losers: {len(losers)}
Best Performer: {best['symbol']} (+{best.get('change_percent', 0):.2f}%) if best else 'N/A'
Worst Performer: {worst['symbol']} ({worst.get('change_percent', 0):.2f}%) if worst else 'N/A'

KEY NEWS:
{chr(10).join([f"- {news.get('title', 'N/A')}" for news in market_news[:3]])}
"""
        
        system_prompt = """You are ATLAS, an AI Financial Assistant providing an evening market summary.

Create a concise evening summary that includes:
1. **Market Recap**: How the market performed today
2. **Your Watchlist**: Summary of your tracked stocks' performance
3. **Key Takeaways**: 2-3 important things that happened today
4. **Tomorrow's Focus**: What to watch for tomorrow

Be concise (under 250 words), professional, and focus on what matters."""
        
        summary = await self.ai_provider.generate_response(
            prompt=f"Generate evening summary:\n{summary_context}",
            context=system_prompt,
            temperature=0.6
        )
        
        return {
            "type": "evening_summary",
            "summary": summary,
            "data": {
                "market_movers": market_movers,
                "watchlist_performance": watchlist_performance,
                "watchlist_summary": {
                    "gainers": len(gainers),
                    "losers": len(losers),
                    "best": best,
                    "worst": worst
                }
            },
            "generated_at": datetime.now().isoformat()
        }
    
    async def generate_watchlist_alerts_summary(self, user_id: int) -> Dict[str, Any]:
        """Generate summary of watchlist alerts and movements."""
        watchlist_items = self.watchlist_repo.get_user_watchlist(user_id)
        
        significant_movements = []
        for item in watchlist_items:
            price_data = await self.market_data.get_stock_price(item.symbol)
            if price_data.get("available"):
                change_percent = price_data.get("change_percent", 0)
                if abs(change_percent) >= 3.0:  # 3% or more movement
                    significant_movements.append({
                        "symbol": item.symbol,
                        "change_percent": change_percent,
                        "current_price": price_data.get("current_price")
                    })
        
        # Sort by absolute change
        significant_movements.sort(key=lambda x: abs(x["change_percent"]), reverse=True)
        
        if not significant_movements:
            return {
                "type": "watchlist_alerts",
                "summary": "No significant movements in your watchlist today.",
                "movements": [],
                "generated_at": datetime.now().isoformat()
            }
        
        context = f"""WATCHLIST ALERTS SUMMARY

Significant Movements (3%+):
{chr(10).join([f"{m['symbol']}: {m['change_percent']:.2f}% (Current: {m['current_price']})" for m in significant_movements])}
"""
        
        system_prompt = """You are ATLAS, an AI Financial Assistant providing watchlist alerts.

Provide a concise summary of significant movements in the user's watchlist. Focus on:
1. Which stocks moved significantly
2. What might be causing the movement
3. Whether this warrants attention

Be concise and actionable."""
        
        summary = await self.ai_provider.generate_response(
            prompt=f"Generate watchlist alerts summary:\n{context}",
            context=system_prompt,
            temperature=0.6
        )
        
        return {
            "type": "watchlist_alerts",
            "summary": summary,
            "movements": significant_movements,
            "generated_at": datetime.now().isoformat()
        }
    
    async def generate_custom_briefing(
        self,
        user_id: int,
        focus: str = "general",
        symbols: Optional[list] = None
    ) -> Dict[str, Any]:
        """Generate custom briefing based on user preferences."""
        if symbols:
            # Focus on specific symbols
            symbol_data = []
            for symbol in symbols:
                price_data = await self.market_data.get_stock_price(symbol)
                company_news = await self.news_service.get_company_news(symbol, limit=3)
                symbol_data.append({
                    "symbol": symbol,
                    "price_data": price_data,
                    "news": company_news
                })
            
            context = f"""CUSTOM BRIEFING - {focus.upper()}

{chr(10).join([f"""
{data['symbol']}:
Price: {data['price_data'].get('current_price', 'N/A')}
Change: {data['price_data'].get('change_percent', 0):.2f}%
Recent News:
{chr(10).join([f"- {news.get('title', 'N/A')}" for news in data['news'][:2]])}
""" for data in symbol_data])}
"""
        else:
            # General briefing
            market_overview = await self.market_data.get_market_overview("^GSPC")
            market_news = await self.news_service.get_market_news(limit=5)
            
            context = f"""CUSTOM BRIEFING - {focus.upper()}

Market: S&P 500 at {market_overview.get('current_price', 'N/A')} ({market_overview.get('change_percent', 0):.2f}%)

Recent News:
{chr(10).join([f"- {news.get('title', 'N/A')}" for news in market_news[:5]])}
"""
        
        system_prompt = f"""You are ATLAS, an AI Financial Assistant providing a custom briefing focused on {focus}.

Provide a concise, relevant briefing that focuses on what matters for the specified topic. Be specific and actionable."""
        
        briefing = await self.ai_provider.generate_response(
            prompt=f"Generate custom briefing:\n{context}",
            context=system_prompt,
            temperature=0.6
        )
        
        return {
            "type": "custom_briefing",
            "focus": focus,
            "briefing": briefing,
            "generated_at": datetime.now().isoformat()
        }
