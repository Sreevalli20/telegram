from typing import Optional, Dict, Any
from app.ai.providers import BaseAIProvider


class FinanceAgent:
    """Agent for financial research and analysis."""
    
    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider
    
    async def analyze_stock(
        self,
        symbol: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Analyze a stock based on the symbol."""
        system_prompt = f"""You are a professional financial analyst. Analyze {symbol.upper()} with a focus on {analysis_type} analysis.

Provide a comprehensive analysis including:
1. Company overview
2. Recent performance
3. Key financial metrics
4. Risk factors
5. Investment considerations

Be specific and data-driven. If you don't have access to real-time data, clearly state that and provide general analysis based on historical knowledge."""
        
        response = await self.ai_provider.generate_response(
            prompt=f"Analyze {symbol.upper()}",
            context=system_prompt,
            temperature=0.5
        )
        
        return {
            "symbol": symbol.upper(),
            "analysis_type": analysis_type,
            "analysis": response,
            "confidence": 0.8  # Placeholder - would be calculated based on data availability
        }
    
    async def get_market_overview(self, focus: str = "general") -> str:
        """Get market overview and trends."""
        system_prompt = f"""You are a financial market analyst. Provide a market overview focusing on {focus}.

Include:
- Major market indices performance
- Key sector trends
- Economic indicators
- Notable market movements

If you don't have access to real-time data, clearly state that and provide general market context."""
        
        response = await self.ai_provider.generate_response(
            prompt="Provide current market overview",
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
    ) -> str:
        """Compare multiple companies."""
        metrics_str = ", ".join(comparison_metrics) if comparison_metrics else "key financial metrics"
        symbols_str = ", ".join([s.upper() for s in symbols])
        
        system_prompt = f"""You are a financial analyst. Compare {symbols_str} based on {metrics_str}.

Provide a structured comparison with:
- Valuation metrics
- Growth metrics
- Profitability metrics
- Risk metrics
- Investment considerations

If you don't have access to real-time data, clearly state that and provide general comparison framework."""
        
        response = await self.ai_provider.generate_response(
            prompt=f"Compare {symbols_str}",
            context=system_prompt,
            temperature=0.5
        )
        
        return response
    
    async def get_financial_news(self, topic: Optional[str] = None) -> str:
        """Get financial news summary."""
        topic_str = f" related to {topic}" if topic else ""
        
        system_prompt = f"""You are a financial news analyst. Provide a summary of recent financial news{topic_str}.

Include:
- Major market-moving events
- Company-specific news
- Economic developments
- Sector trends

If you don't have access to real-time news, clearly state that and provide general market context."""
        
        response = await self.ai_provider.generate_response(
            prompt=f"Summarize recent financial news{topic_str}",
            context=system_prompt,
            temperature=0.5
        )
        
        return response
