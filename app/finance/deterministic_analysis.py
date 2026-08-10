"""Deterministic financial analysis without AI dependency."""
from typing import Dict, Any, Optional


class DeterministicAnalysis:
    """Provides deterministic financial analysis based on data only, no AI required."""
    
    @staticmethod
    def analyze_stock_data(stock_data: Dict[str, Any]) -> str:
        """Generate analysis from stock data using deterministic rules."""
        if not stock_data.get("available", True):
            return "Unable to fetch stock data. Please check the symbol and try again."
        
        symbol = stock_data.get("symbol", "N/A")
        current_price = stock_data.get("current_price")
        previous_close = stock_data.get("previous_close")
        change = stock_data.get("change")
        change_percent = stock_data.get("change_percent")
        volume = stock_data.get("volume")
        market_cap = stock_data.get("market_cap")
        
        lines = [f"📊 {symbol.upper()} Stock Analysis"]
        lines.append("")
        
        # Price information
        if current_price:
            lines.append(f"Current Price: ${current_price:.2f}")
            if previous_close:
                lines.append(f"Previous Close: ${previous_close:.2f}")
        
        # Daily performance
        if change is not None and change_percent is not None:
            lines.append("")
            if change >= 0:
                lines.append(f"Daily Change: +${change:.2f} (+{change_percent:.2f}%) 📈")
            else:
                lines.append(f"Daily Change: ${change:.2f} ({change_percent:.2f}%) 📉")
        
        # Volume analysis
        if volume:
            volume_str = f"{volume:,.0f}"
            lines.append(f"Volume: {volume_str}")
        
        # Market cap
        if market_cap:
            if market_cap >= 1e12:
                mc_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                mc_str = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                mc_str = f"${market_cap/1e6:.2f}M"
            else:
                mc_str = f"${market_cap:,.0f}"
            lines.append(f"Market Cap: {mc_str}")
        
        # Simple trend indicator
        lines.append("")
        if change_percent is not None:
            if change_percent > 2:
                lines.append("Trend: Strong positive movement today")
            elif change_percent > 0:
                lines.append("Trend: Slight positive movement today")
            elif change_percent > -2:
                lines.append("Trend: Slight negative movement today")
            else:
                lines.append("Trend: Strong negative movement today")
        
        lines.append("")
        lines.append("Note: This is basic data analysis. For advanced AI-powered insights, configure GOOGLE_API_KEY.")
        
        return "\n".join(lines)
    
    @staticmethod
    def explain_pe_ratio() -> str:
        """Explain P/E ratio deterministically."""
        return """📚 P/E Ratio (Price-to-Earnings Ratio)

The P/E ratio measures a company's current share price relative to its per-share earnings.

Formula: P/E = Stock Price / Earnings Per Share (EPS)

What it tells you:
• High P/E: Investors expect high growth (or stock is overvalued)
• Low P/E: Stock may be undervalued or company is struggling
• Industry comparison is important (tech stocks typically have higher P/E than utilities)

Example:
If a stock trades at $100 and earns $5 per share, P/E = 20

This means investors are willing to pay $20 for every $1 of earnings."""
    
    @staticmethod
    def explain_dividend() -> str:
        """Explain dividends deterministically."""
        return """📚 Dividend

A dividend is a portion of a company's earnings distributed to shareholders.

Key terms:
• Dividend Yield: Annual dividend / Current stock price
• Ex-Dividend Date: Must own stock before this date to receive dividend
• Payout Ratio: Percentage of earnings paid as dividends

Example:
If a stock pays $2 annually and trades at $100, the yield is 2%

Dividends provide regular income but aren't guaranteed - companies can cut them."""
    
    @staticmethod
    def explain_market_cap() -> str:
        """Explain market cap deterministically."""
        return """📚 Market Capitalization (Market Cap)

The total value of a company's outstanding shares of stock.

Calculation: Market Cap = Share Price × Total Outstanding Shares

Categories:
• Mega-cap: $200B+ (e.g., Apple, Microsoft)
• Large-cap: $10B - $200B
• Mid-cap: $2B - $10B
• Small-cap: $300M - $2B
• Micro-cap: Under $300M

Market cap indicates company size and stability, but not necessarily investment quality."""
    
    @staticmethod
    def get_help_text() -> str:
        """Return help text for the bot."""
        return """🤖 Atlas Financial Assistant - Help

I can help you with:

📈 Stock Information:
• "AAPL" or "Apple" - Get stock price and basic data
• "analyze Apple stock" - Detailed stock analysis
• "price of Tesla" - Current stock price

📊 Market Data:
• "market overview" - General market trends
• "compare Apple and Microsoft" - Compare companies

📚 Financial Education:
• "What is P/E ratio?" - Learn financial concepts
• "explain dividends" - Understand dividends
• "what is market cap?" - Learn about market cap

💬 Conversation:
• "hello" or "hi" - Greet me
• "help" - Show this help message

Note: Advanced AI features require GOOGLE_API_KEY. Basic stock data and explanations work without it."""
    
    @staticmethod
    def get_greeting() -> str:
        """Return a friendly greeting."""
        return """👋 Hello! I'm Atlas, your financial assistant.

I can help you with stock information, market data, and financial education.

Try commands like:
• "AAPL" or "Apple" - Get stock price
• "analyze Apple stock" - Detailed analysis
• "What is P/E ratio?" - Learn financial concepts
• "help" - See all available commands

Type "help" anytime to see what I can do!"""
    
    @staticmethod
    def get_unknown_response() -> str:
        """Return response for unknown queries without AI."""
        return """🤔 I'm not sure how to help with that right now.

Without AI configured, I can assist with:
• Stock prices and basic data (e.g., "AAPL", "Apple")
• Financial concepts (e.g., "What is P/E ratio?")
• Market overview

For advanced conversational AI, configure GOOGLE_API_KEY.

Type "help" to see available commands."""
