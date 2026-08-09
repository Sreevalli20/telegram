from typing import Optional, Dict, Any, List
from app.ai.providers import BaseAIProvider
from app.finance import MarketDataService, CompanyDataService, NewsService, AnalyticsService
from app.utils.ai_safety import get_safety_context, validate_financial_response


class FinanceAgent:
    """Agent for financial research and analysis with real data integration."""
    
    def __init__(self, ai_provider: Optional[BaseAIProvider] = None):
        self.ai_provider = ai_provider
        self.market_data = MarketDataService()
        self.company_data = CompanyDataService()
        self.news_service = NewsService()
        self.analytics = AnalyticsService(self.market_data, self.company_data)
    
    async def analyze_stock(
        self,
        symbol: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Analyze a stock based on the symbol with real data integration."""
        # Fetch real data
        stock_price = await self.market_data.get_stock_price(symbol)
        company_overview = await self.company_data.get_company_overview(symbol)
        financial_metrics = await self.company_data.get_financial_metrics(symbol)
        company_news = await self.news_service.get_company_news(symbol, limit=5)
        
        # Build context for AI
        data_context = f"""Stock Data for {symbol.upper()}:
Current Price: {stock_price.get('current_price', 'N/A')}
Change: {stock_price.get('change', 'N/A')} ({stock_price.get('change_percent', 'N/A')}%)
Market Cap: {stock_price.get('market_cap', 'N/A')}

Company: {company_overview.get('company_name', 'N/A')}
Industry: {company_overview.get('industry', 'N/A')}
Sector: {company_overview.get('sector', 'N/A')}

Key Metrics:
P/E Ratio: {financial_metrics.get('trailing_pe', 'N/A')}
Profit Margin: {financial_metrics.get('profit_margin', 'N/A')}
ROE: {financial_metrics.get('return_on_equity', 'N/A')}
Debt to Equity: {financial_metrics.get('debt_to_equity', 'N/A')}

Recent News Headlines:
{chr(10).join([f"- {news.get('title', 'N/A')}" for news in company_news[:3]])}
"""
        
        system_prompt = f"""You are a professional financial analyst. Analyze {symbol.upper()} with a focus on {analysis_type} analysis.

Use the provided real data to give specific, data-driven insights. Include:
1. Company overview and business model
2. Recent performance based on the data
3. Key financial metrics interpretation
4. Risk factors based on the data
5. Investment considerations

{get_safety_context()}

Be concise and specific. If data is unavailable, clearly state that limitation."""
        
        response = await self.ai_provider.generate_response(
            prompt=f"Analyze {symbol.upper()} using this data:\n{data_context}",
            context=system_prompt,
            temperature=0.5
        )
        
        return {
            "symbol": symbol.upper(),
            "analysis_type": analysis_type,
            "analysis": response,
            "data": {
                "stock_price": stock_price,
                "company_overview": company_overview,
                "financial_metrics": financial_metrics,
                "news": company_news
            },
            "confidence": 0.9 if stock_price.get("available") else 0.6
        }
    
    async def get_market_overview(self, focus: str = "general") -> str:
        """Get market overview and trends with real data."""
        # Fetch real market data
        market_movers = await self.market_data.get_market_movers(market="US", limit=5)
        sector_performance = await self.market_data.get_sector_performance(market="US")
        market_news = await self.news_service.get_market_news(limit=5)
        
        # Build context
        data_context = f"""Market Overview:

Top Gainers:
{chr(10).join([f"{g['symbol']}: {g.get('change_percent', 0):.2f}%" for g in market_movers.get('gainers', [])[:3]])}

Top Losers:
{chr(10).join([f"{l['symbol']}: {l.get('change_percent', 0):.2f}%" for l in market_movers.get('losers', [])[:3]])}

Sector Performance:
{chr(10).join([f"{sector}: {data.get('change_percent', 0):.2f}%" for sector, data in sector_performance.get('sectors', {}).items()])}

Recent News:
{chr(10).join([f"- {news.get('title', 'N/A')}" for news in market_news[:3]])}
"""
        
        system_prompt = f"""You are a financial market analyst. Provide a market overview focusing on {focus}.

Use the provided real data to give specific insights. Include:
- Major market movements based on the data
- Sector trends
- Key market-moving events
- Overall market sentiment

{get_safety_context()}

Be concise and data-driven. If data is unavailable, clearly state that limitation."""
        
        response = await self.ai_provider.generate_response(
            prompt=f"Provide market overview using this data:\n{data_context}",
            context=system_prompt,
            temperature=0.5
        )
        
        return response
    
    async def analyze_earnings(
        self,
        symbol: str,
        quarter: Optional[str] = None
    ) -> str:
        """Analyze earnings for a specific company."""
        quarter_info = f" for {quarter}" if quarter else ""
        
        system_prompt = f"""You are a financial analyst specializing in earnings analysis. Analyze {symbol.upper()}'s earnings{quarter_info}.

Include:
- Revenue vs expectations
- EPS vs expectations
- Guidance
- Key highlights and concerns
- Management commentary

{get_safety_context()}

If you don't have access to the specific earnings data, clearly state that and provide general earnings analysis framework."""
        
        response = await self.ai_provider.generate_response(
            prompt=f"Analyze earnings for {symbol.upper()}{quarter_info}",
            context=system_prompt,
            temperature=0.5
        )
        
        return response
    
    async def compare_companies(
        self,
        symbols: list,
        comparison_metrics: Optional[list] = None
    ) -> Dict[str, Any]:
        """Compare multiple companies with real data."""
        comparison_result = await self.analytics.compare_companies(symbols, comparison_metrics)
        
        if not comparison_result.get("available"):
            return {
                "error": "Could not fetch comparison data",
                "available": False
            }
        
        # Build context for AI
        data_context = f"""Comparison Data for {', '.join(symbols)}:

Company Overviews:
{chr(10).join([f"{s}: {comparison_result['company_overviews'].get(s, {}).get('company_name', 'N/A')}" for s in symbols])}

Comparison Metrics:
"""
        for metric, values in comparison_result.get("comparison", {}).items():
            data_context += f"\n{metric}:\n"
            for symbol, value in values.items():
                data_context += f"  {symbol}: {value}\n"
        
        data_context += f"\nSummary:\n"
        for key, value in comparison_result.get("summary", {}).items():
            data_context += f"{key}: {value}\n"
        
        system_prompt = f"""You are a financial analyst. Compare {', '.join(symbols)} based on the provided real data.

Provide a structured comparison with:
- Company overview
- Valuation analysis
- Growth comparison
- Profitability comparison
- Risk assessment
- Investment considerations

{get_safety_context()}

Be concise and data-driven. Highlight key differences and similarities."""
        
        response = await self.ai_provider.generate_response(
            prompt=f"Compare these companies using this data:\n{data_context}",
            context=system_prompt,
            temperature=0.5
        )
        
        return {
            "symbols": symbols,
            "comparison_analysis": response,
            "data": comparison_result,
            "available": True
        }
    
    async def get_financial_news(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Get financial news summary with real data."""
        if topic:
            news_items = await self.news_service.get_company_news(topic, limit=10)
        else:
            news_items = await self.news_service.get_market_news(limit=10)
        
        sentiment = await self.news_service.analyze_news_sentiment(news_items)
        
        # Build context
        data_context = f"""Financial News Summary:

Total News Items: {len(news_items)}
Sentiment: {sentiment.get('sentiment', 'neutral')} (Positive: {sentiment.get('positive', 0)}, Negative: {sentiment.get('negative', 0)}, Neutral: {sentiment.get('neutral', 0)})

Recent News:
{chr(10).join([f"{i+1}. {news.get('title', 'N/A')}\n   Source: {news.get('source', 'N/A')}\n   {news.get('summary', '')[:100]}..." for i, news in enumerate(news_items[:5])])}
"""
        
        system_prompt = f"""You are a financial news analyst. Provide a summary of recent financial news{f' related to {topic}' if topic else ''}.

Use the provided real news data to give specific insights. Include:
- Major market-moving events
- Key themes and trends
- Overall market sentiment
- Important company-specific developments

Be concise and focus on actionable insights."""
        
        response = await self.ai_provider.generate_response(
            prompt=f"Summarize this financial news:\n{data_context}",
            context=system_prompt,
            temperature=0.5
        )
        
        return {
            "topic": topic,
            "news_summary": response,
            "sentiment": sentiment,
            "news_count": len(news_items),
            "available": True
        }
    
    async def get_company_research(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive company research."""
        # Fetch all company data
        complete_profile = await self.company_data.get_complete_company_profile(symbol)
        valuation = await self.analytics.analyze_valuation(symbol)
        financial_health = await self.analytics.analyze_financial_health(symbol)
        growth = await self.analytics.analyze_growth_trends(symbol)
        investment_thesis = await self.analytics.generate_investment_thesis(symbol)
        
        # Build comprehensive research context
        data_context = f"""Complete Company Research for {symbol.upper()}:

BUSINESS OVERVIEW:
Company: {complete_profile['overview'].get('company_name', 'N/A')}
Industry: {complete_profile['overview'].get('industry', 'N/A')}
Sector: {complete_profile['overview'].get('sector', 'N/A')}
Business: {complete_profile['overview'].get('business_summary', 'N/A')[:300]}...

FINANCIAL HEALTH:
Health Score: {financial_health.get('health_score', 0)}/100
Profit Margin: {financial_health.get('health_metrics', {}).get('profit_margin', 'N/A')}
ROE: {financial_health.get('health_metrics', {}).get('return_on_equity', 'N/A')}
Debt to Equity: {financial_health.get('health_metrics', {}).get('debt_to_equity', 'N/A')}

VALUATION:
P/E: {valuation.get('valuation_metrics', {}).get('trailing_pe', 'N/A')}
P/B: {valuation.get('valuation_metrics', {}).get('price_to_book', 'N/A')}
PEG: {valuation.get('valuation_metrics', {}).get('peg_ratio', 'N/A')}

GROWTH:
Revenue Growth: {growth.get('growth_metrics', {}).get('revenue_growth', 'N/A')}
Earnings Growth: {growth.get('growth_metrics', {}).get('earnings_growth', 'N/A')}

INVESTMENT CONSIDERATIONS:
Strengths: {', '.join(investment_thesis.get('investment_considerations', {}).get('strengths', []))}
Risks: {', '.join(investment_thesis.get('investment_considerations', {}).get('risks', []))}
Opportunities: {', '.join(investment_thesis.get('investment_considerations', {}).get('opportunities', []))}
"""
        
        system_prompt = f"""You are a professional financial analyst providing comprehensive company research for {symbol.upper()}.

Use the provided real data to give specific, actionable insights. Structure your response as:

1. **Business Summary**: What the company does and its position in the industry
2. **Financial Highlights**: Key metrics and what they mean
3. **Growth Drivers**: What's driving the company's growth
4. **Major Risks**: Key risks investors should consider
5. **Investment Perspective**: Balanced view of the investment case
6. **Key Questions**: Important questions investors should ask

{get_safety_context()}

Be concise, specific, and data-driven. Avoid generic advice. If data is unavailable, clearly state that limitation."""
        
        response = await self.ai_provider.generate_response(
            prompt=f"Provide comprehensive company research using this data:\n{data_context}",
            context=system_prompt,
            temperature=0.5
        )
        
        return {
            "symbol": symbol.upper(),
            "research": response,
            "data": {
                "complete_profile": complete_profile,
                "valuation": valuation,
                "financial_health": financial_health,
                "growth": growth,
                "investment_thesis": investment_thesis
            },
            "available": complete_profile.get("overview", {}).get("available", False)
        }
    
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get current stock price with context."""
        price_data = await self.market_data.get_stock_price(symbol)
        
        if not price_data.get("available"):
            return {
                "symbol": symbol.upper(),
                "error": "Could not fetch price data",
                "available": False
            }
        
        # Build context
        data_context = f"""Stock Price for {symbol.upper()}:
Current Price: {price_data.get('current_price', 'N/A')}
Previous Close: {price_data.get('previous_close', 'N/A')}
Change: {price_data.get('change', 'N/A')}
Change %: {price_data.get('change_percent', 'N/A')}%
Volume: {price_data.get('volume', 'N/A')}
Market Cap: {price_data.get('market_cap', 'N/A')}
"""
        
        system_prompt = f"""You are a financial analyst. Provide the current stock price for {symbol.upper()} with context.

Use the provided data to give:
1. Current price and movement
2. What the price movement means
3. Volume analysis if significant
4. Any notable patterns

Be concise and specific."""
        
        response = await self.ai_provider.generate_response(
            prompt=f"Provide stock price analysis using this data:\n{data_context}",
            context=system_prompt,
            temperature=0.5
        )
        
        return {
            "symbol": symbol.upper(),
            "price_analysis": response,
            "price_data": price_data,
            "available": True
        }
