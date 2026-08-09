"""Response formatter service for enhancing product experience with formatting and follow-up suggestions."""
from typing import Dict, Any, List, Optional


class ResponseFormatter:
    """Service for formatting responses and enhancing user experience."""
    
    def __init__(self):
        self.emojis = {
            "stock": "📈",
            "market": "📊",
            "news": "📰",
            "alert": "🚨",
            "watchlist": "⭐",
            "document": "📄",
            "comparison": "⚖️",
            "earnings": "💰",
            "risk": "⚠️",
            "opportunity": "🎯",
            "insight": "💡",
            "success": "✅",
            "error": "❌",
            "info": "ℹ️",
            "question": "❓"
        }
    
    def format_response(
        self,
        content: str,
        intent: Optional[str] = None,
        include_emoji: bool = True,
        include_suggestions: bool = True,
        suggestions: Optional[List[str]] = None
    ) -> str:
        """Format a response with appropriate formatting and suggestions."""
        formatted = content
        
        # Add emoji based on intent
        if include_emoji and intent:
            emoji = self._get_emoji_for_intent(intent)
            if emoji:
                formatted = f"{emoji} {formatted}"
        
        # Format with markdown for readability
        formatted = self._apply_markdown_formatting(formatted)
        
        # Add follow-up suggestions
        if include_suggestions and suggestions:
            formatted = self._add_suggestions(formatted, suggestions)
        
        return formatted
    
    def _get_emoji_for_intent(self, intent: str) -> str:
        """Get appropriate emoji for intent."""
        emoji_map = {
            "stock_lookup": self.emojis["stock"],
            "company_research": self.emojis["stock"],
            "market_analysis": self.emojis["market"],
            "news_request": self.emojis["news"],
            "watchlist": self.emojis["watchlist"],
            "alert": self.emojis["alert"],
            "document_analysis": self.emojis["document"],
            "comparison": self.emojis["comparison"],
            "earnings": self.emojis["earnings"],
            "explanation": self.emojis["insight"]
        }
        return emoji_map.get(intent, "")
    
    def _apply_markdown_formatting(self, text: str) -> str:
        """Apply markdown formatting for better readability."""
        # Bold key terms (simple heuristic)
        key_terms = [
            "Revenue", "Profit", "EPS", "P/E", "ROE", "Debt", "Cash Flow",
            "Growth", "Risk", "Valuation", "Market Cap", "Dividend"
        ]
        
        for term in key_terms:
            text = text.replace(term, f"**{term}**")
        
        # Format sections with headers
        lines = text.split("\n")
        formatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            # Detect section headers (numbered or all caps)
            if stripped and (stripped[0].isdigit() or stripped.isupper() or stripped.endswith(":")):
                if not stripped.startswith("**"):
                    line = f"\n**{stripped}**"
            formatted_lines.append(line)
        
        return "\n".join(formatted_lines)
    
    def _add_suggestions(self, content: str, suggestions: List[str]) -> str:
        """Add follow-up suggestions to response."""
        if not suggestions:
            return content
        
        suggestions_text = "\n\n💡 **Follow-up questions:**\n"
        for i, suggestion in enumerate(suggestions, 1):
            suggestions_text += f"{i}. {suggestion}\n"
        
        return content + suggestions_text
    
    def format_stock_response(
        self,
        symbol: str,
        price_data: Dict[str, Any],
        analysis: str
    ) -> str:
        """Format stock-specific response with data."""
        change_emoji = "📈" if price_data.get("change_percent", 0) > 0 else "📉"
        
        header = f"{change_emoji} **{symbol}** - ${price_data.get('current_price', 'N/A')}"
        if price_data.get("change_percent") is not None:
            header += f" ({price_data['change_percent']:+.2f}%)"
        
        formatted = f"{header}\n━━━━━━━━━━━━━━━━━━\n\n{analysis}"
        
        return formatted
    
    def format_watchlist_response(self, watchlist_data: List[Dict[str, Any]]) -> str:
        """Format watchlist response."""
        if not watchlist_data:
            return "⭐ Your watchlist is empty. Add stocks to track them!"
        
        header = f"⭐ **Your Watchlist** ({len(watchlist_data)} items)\n━━━━━━━━━━━━━━━━━━\n\n"
        
        items = []
        for item in watchlist_data:
            change_emoji = "📈" if item.get("change_percent", 0) > 0 else "📉"
            item_text = f"{change_emoji} **{item['symbol']}**"
            if item.get("current_price"):
                item_text += f" - ${item['current_price']}"
            if item.get("change_percent") is not None:
                item_text += f" ({item['change_percent']:+.2f}%)"
            items.append(item_text)
        
        return header + "\n".join(items)
    
    def format_news_response(self, news_items: List[Dict[str, Any]], sentiment: str) -> str:
        """Format news response with sentiment."""
        sentiment_emoji = {
            "positive": "🟢",
            "negative": "🔴",
            "neutral": "⚪"
        }
        
        header = f"📰 **Market News** {sentiment_emoji.get(sentiment, '')}\n━━━━━━━━━━━━━━━━━━\n\n"
        
        items = []
        for i, news in enumerate(news_items[:5], 1):
            item_text = f"{i}. **{news.get('title', 'N/A')}**\n"
            if news.get("source"):
                item_text += f"   Source: {news['source']}\n"
            items.append(item_text)
        
        return header + "\n".join(items)
    
    def format_error_response(self, error_message: str, suggestion: Optional[str] = None) -> str:
        """Format error response helpfully."""
        response = f"❌ **Error**: {error_message}\n"
        
        if suggestion:
            response += f"\n💡 **Suggestion**: {suggestion}"
        
        return response
    
    def format_comparison_response(
        self,
        symbols: List[str],
        comparison_data: Dict[str, Any]
    ) -> str:
        """Format comparison response."""
        header = f"⚖️ **Comparison**: {', '.join(symbols)}\n━━━━━━━━━━━━━━━━━━\n\n"
        
        # Add summary if available
        if comparison_data.get("summary"):
            summary_section = "**Summary**\n"
            for key, value in comparison_data["summary"].items():
                summary_section += f"• {key}: {value}\n"
            header += summary_section + "\n"
        
        return header + comparison_data.get("comparison_analysis", "")
    
    def generate_suggestions(
        self,
        intent: str,
        symbol: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate contextual follow-up suggestions."""
        suggestions = []
        
        if intent == "company_research" and symbol:
            suggestions = [
                f"Compare {symbol} with competitors",
                f"What are the risks for {symbol}?",
                f"Is {symbol} overvalued or undervalued?",
                f"Add {symbol} to my watchlist"
            ]
        elif intent == "stock_lookup":
            suggestions = [
                "Show company overview",
                "View financial metrics",
                "Check recent news",
                "Add to watchlist"
            ]
        elif intent == "market_analysis":
            suggestions = [
                "Show top gainers and losers",
                "Sector performance",
                "Market sentiment analysis",
                "Economic calendar"
            ]
        elif intent == "comparison":
            suggestions = [
                "Detailed financial comparison",
                "Valuation analysis",
                "Growth comparison"
            ]
        elif intent == "watchlist":
            suggestions = [
                "Add another stock",
                "Set price alerts",
                "View watchlist performance"
            ]
        elif intent == "news_request":
            suggestions = [
                "Filter by sector",
                "Company-specific news",
                "Earnings calendar"
            ]
        else:
            suggestions = [
                "Analyze a stock",
                "Market overview",
                "My watchlist",
                "Recent news"
            ]
        
        return suggestions[:3]
    
    def truncate_response(self, response: str, max_length: int = 3000) -> str:
        """Truncate response if too long for Telegram."""
        if len(response) <= max_length:
            return response
        
        truncated = response[:max_length - 100]
        truncated += "\n\n... (response truncated due to length. Ask for more details if needed.)"
        
        return truncated
