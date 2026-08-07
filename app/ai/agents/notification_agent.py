from typing import List, Dict, Any
from app.ai.providers import BaseAIProvider


class NotificationAgent:
    """Agent for generating and managing notifications."""
    
    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider
    
    async def generate_price_alert_message(
        self,
        symbol: str,
        current_price: float,
        target_price: float,
        alert_type: str  # "above" or "below"
    ) -> str:
        """Generate a price alert notification message."""
        direction = "reached above" if alert_type == "above" else "fallen below"
        
        message = f"""🔔 Price Alert: {symbol.upper()}
        
Current Price: ${current_price:.2f}
Target Price: ${target_price:.2f}

{symbol.upper()} has {direction} your target price.

Would you like me to provide an analysis of this movement?"""
        
        return message
    
    async def generate_earnings_alert(
        self,
        symbol: str,
        earnings_date: str
    ) -> str:
        """Generate an earnings announcement alert."""
        message = f"""📊 Earnings Alert: {symbol.upper()}
        
Earnings Announcement: {earnings_date}

{symbol.upper()} is reporting earnings soon.

Would you like me to:
- Provide analyst expectations
- Show recent performance
- Set up post-earnings analysis?"""
        
        return message
    
    async def generate_news_alert(
        self,
        symbol: str,
        headline: str,
        summary: str
    ) -> str:
        """Generate a news alert notification."""
        message = f"""📰 News Alert: {symbol.upper()}
        
{headline}

{summary}

Would you like me to analyze the potential impact?"""
        
        return message
    
    async def generate_market_summary(
        self,
        market_data: Dict[str, Any]
    ) -> str:
        """Generate a daily market summary notification."""
        system_prompt = """You are a financial analyst. Generate a concise daily market summary.

Include:
- Major index movements
- Key sector performance
- Notable stock movements
- Economic indicators

Keep it under 200 words."""
        
        market_text = str(market_data)
        
        response = await self.ai_provider.generate_response(
            prompt="Generate daily market summary",
            context=system_prompt + "\n\n" + market_text,
            temperature=0.5
        )
        
        return response
    
    async def prioritize_notifications(
        self,
        notifications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prioritize notifications based on user preferences and urgency."""
        # Simple prioritization logic
        priority_order = {
            "price_alert": 1,
            "earnings": 2,
            "news": 3,
            "market_summary": 4
        }
        
        sorted_notifications = sorted(
            notifications,
            key=lambda x: priority_order.get(x.get("type", "market_summary"), 5)
        )
        
        return sorted_notifications
