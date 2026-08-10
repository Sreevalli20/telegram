"""Deterministic financial analysis without AI dependency."""
from typing import Dict, Any, Optional


class DeterministicAnalysis:
    """Provides deterministic financial analysis based on data only, no AI required."""
    
    @staticmethod
    def analyze_stock_data(stock_data: Dict[str, Any], company_data: Optional[Dict[str, Any]] = None, financial_metrics: Optional[Dict[str, Any]] = None) -> str:
        """Generate comprehensive analysis from stock data using deterministic rules."""
        if not stock_data.get("available", True):
            return "Unable to fetch stock data. Please check the symbol and try again."
        
        symbol = stock_data.get("symbol", "N/A")
        current_price = stock_data.get("current_price")
        previous_close = stock_data.get("previous_close")
        change = stock_data.get("change")
        change_percent = stock_data.get("change_percent")
        volume = stock_data.get("volume")
        market_cap = stock_data.get("market_cap")
        
        lines = [f"� {symbol.upper()}"]
        lines.append("")
        
        # Company name if available
        if company_data and company_data.get("company_name"):
            lines.append(f"Company: {company_data['company_name']}")
            if company_data.get("industry"):
                lines.append(f"Industry: {company_data['industry']}")
            lines.append("")
        
        # Price information
        if current_price:
            lines.append(f"💰 Price: ${current_price:.2f}")
            if previous_close:
                lines.append(f"Previous Close: ${previous_close:.2f}")
        
        # Daily performance
        if change is not None and change_percent is not None:
            lines.append("")
            if change >= 0:
                lines.append(f"Day Change: +${change:.2f} (+{change_percent:.2f}%) 📈")
            else:
                lines.append(f"Day Change: ${change:.2f} ({change_percent:.2f}%) 📉")
        
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
        
        # Financial metrics if available
        if financial_metrics and financial_metrics.get("available"):
            lines.append("")
            lines.append("📊 Key Metrics:")
            
            pe_ratio = financial_metrics.get("trailing_pe")
            if pe_ratio:
                lines.append(f"P/E Ratio: {pe_ratio:.2f}")
            
            dividend_yield = financial_metrics.get("dividend_yield")
            if dividend_yield:
                lines.append(f"Dividend Yield: {dividend_yield*100:.2f}%")
            
            profit_margin = financial_metrics.get("profit_margin")
            if profit_margin:
                lines.append(f"Profit Margin: {profit_margin*100:.2f}%")
            
            roe = financial_metrics.get("return_on_equity")
            if roe:
                lines.append(f"ROE: {roe*100:.2f}%")
        
        # Trend analysis
        lines.append("")
        lines.append("📊 Trend Analysis:")
        if change_percent is not None:
            if change_percent > 5:
                lines.append("• Strong positive momentum today")
            elif change_percent > 2:
                lines.append("• Moderate positive movement today")
            elif change_percent > 0:
                lines.append("• Slight positive movement today")
            elif change_percent > -2:
                lines.append("• Slight negative movement today")
            elif change_percent > -5:
                lines.append("• Moderate negative movement today")
            else:
                lines.append("• Strong negative pressure today")
        
        # Valuation insight
        if financial_metrics and financial_metrics.get("trailing_pe"):
            pe = financial_metrics["trailing_pe"]
            lines.append("")
            lines.append("💰 Valuation:")
            if pe < 15:
                lines.append(f"• P/E of {pe:.1f} suggests potential value or low growth expectations")
            elif pe < 25:
                lines.append(f"• P/E of {pe:.1f} indicates moderate valuation")
            elif pe < 40:
                lines.append(f"• P/E of {pe:.1f} suggests growth expectations")
            else:
                lines.append(f"• P/E of {pe:.1f} indicates high growth expectations or potential overvaluation")
        
        # Key observations
        lines.append("")
        lines.append("📌 Key Observations:")
        if change_percent is not None:
            if abs(change_percent) > 3:
                lines.append("• Significant price movement today - check recent news")
            else:
                lines.append("• Normal trading activity")
        
        if volume and market_cap:
            # Rough volume/market cap ratio
            volume_ratio = volume / market_cap if market_cap > 0 else 0
            if volume_ratio > 0.01:  # More than 1% of market cap traded
                lines.append("• High trading volume relative to market cap")
            else:
                lines.append("• Normal trading volume")
        
        lines.append("")
        lines.append("⚠️ Note: This is data-based analysis, not personalized investment advice.")
        
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

📋 Watchlist:
• "my watchlist" - View your watchlist
• "add AAPL to watchlist" - Add a stock

All core features work without any AI API required!"""
    
    @staticmethod
    def get_greeting() -> str:
        """Return a friendly greeting."""
        return """👋 Hello! I'm Atlas, your financial assistant.

I can help you with stock information, market data, and financial concepts - all without requiring AI!

Try commands like:
• "AAPL" or "Apple" - Get stock price
• "analyze Apple stock" - Detailed analysis
• "What is P/E ratio?" - Learn financial concepts
• "market overview" - Market data
• "help" - See all available commands

What would you like to know?"""
    
    @staticmethod
    def get_unknown_response() -> str:
        """Return response for unknown queries without AI."""
        return """🤔 I'm not sure how to help with that specific request.

Try asking about:
• Stock prices: "AAPL" or "Apple stock"
• Market data: "market overview"
• Financial concepts: "What is P/E ratio?"
• Stock analysis: "analyze Apple stock"
• Comparisons: "compare Apple and Microsoft"

Type "help" to see all available commands."""
