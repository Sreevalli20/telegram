"""Financial analytics service for analysis and insights."""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio


class AnalyticsService:
    """Service for financial analytics and comparative analysis."""
    
    def __init__(self, market_data_service, company_data_service):
        self.market_data = market_data_service
        self.company_data = company_data_service
    
    async def compare_companies(
        self, 
        symbols: List[str], 
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Compare multiple companies across specified metrics."""
        if not symbols or len(symbols) < 2:
            return {
                "error": "At least 2 symbols required for comparison",
                "available": False
            }
        
        # Default metrics to compare
        default_metrics = [
            "market_cap", "trailing_pe", "forward_pe", "profit_margin",
            "return_on_equity", "debt_to_equity", "revenue_growth", "earnings_growth"
        ]
        
        comparison_metrics = metrics or default_metrics
        
        # Fetch data for all companies
        tasks = [
            self.company_data.get_financial_metrics(symbol) 
            for symbol in symbols
        ]
        results = await asyncio.gather(*tasks)
        
        # Build comparison matrix
        comparison = {
            "symbols": symbols,
            "metrics": comparison_metrics,
            "comparison": {},
            "summary": {},
            "available": True
        }
        
        for metric in comparison_metrics:
            comparison["comparison"][metric] = {}
            for symbol, result in zip(symbols, results):
                if result.get("available"):
                    comparison["comparison"][metric][symbol] = result.get(metric)
        
        # Add company overviews
        overview_tasks = [
            self.company_data.get_company_overview(symbol) 
            for symbol in symbols
        ]
        overviews = await asyncio.gather(*overview_tasks)
        
        comparison["company_overviews"] = {}
        for symbol, overview in zip(symbols, overviews):
            comparison["company_overviews"][symbol] = overview
        
        # Generate summary insights
        comparison["summary"] = self._generate_comparison_summary(
            symbols, comparison["comparison"]
        )
        
        return comparison
    
    def _generate_comparison_summary(
        self, 
        symbols: List[str], 
        comparison_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, str]:
        """Generate summary insights from comparison data."""
        summary = {}
        
        # Valuation comparison
        if "trailing_pe" in comparison_data:
            pe_data = comparison_data["trailing_pe"]
            valid_pe = {k: v for k, v in pe_data.items() if v is not None}
            if valid_pe:
                lowest_pe = min(valid_pe.items(), key=lambda x: x[1])
                highest_pe = max(valid_pe.items(), key=lambda x: x[1])
                summary["valuation"] = f"{lowest_pe[0]} has the lowest P/E ({lowest_pe[1]:.2f}), while {highest_pe[0]} has the highest ({highest_pe[1]:.2f})"
        
        # Profitability comparison
        if "profit_margin" in comparison_data:
            margin_data = comparison_data["profit_margin"]
            valid_margin = {k: v for k, v in margin_data.items() if v is not None}
            if valid_margin:
                highest_margin = max(valid_margin.items(), key=lambda x: x[1])
                summary["profitability"] = f"{highest_margin[0]} has the highest profit margin ({highest_margin[1]*100:.2f}%)"
        
        # Growth comparison
        if "earnings_growth" in comparison_data:
            growth_data = comparison_data["earnings_growth"]
            valid_growth = {k: v for k, v in growth_data.items() if v is not None}
            if valid_growth:
                highest_growth = max(valid_growth.items(), key=lambda x: x[1])
                summary["growth"] = f"{highest_growth[0]} has the highest earnings growth ({highest_growth[1]*100:.2f}%)"
        
        return summary
    
    async def analyze_valuation(self, symbol: str) -> Dict[str, Any]:
        """Analyze valuation metrics for a company."""
        metrics = await self.company_data.get_financial_metrics(symbol)
        
        if not metrics.get("available"):
            return metrics
        
        analysis = {
            "symbol": symbol,
            "valuation_metrics": {
                "trailing_pe": metrics.get("trailing_pe"),
                "forward_pe": metrics.get("forward_pe"),
                "peg_ratio": metrics.get("peg_ratio"),
                "price_to_book": metrics.get("price_to_book"),
                "price_to_sales": metrics.get("price_to_sales"),
                "enterprise_to_ebitda": metrics.get("enterprise_to_ebitda")
            },
            "interpretation": self._interpret_valuation(metrics),
            "available": True
        }
        
        return analysis
    
    def _interpret_valuation(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Interpret valuation metrics."""
        interpretation = {}
        
        pe = metrics.get("trailing_pe")
        if pe:
            if pe < 15:
                interpretation["pe_ratio"] = "Low P/E suggests the stock may be undervalued or the company has low growth expectations"
            elif pe < 25:
                interpretation["pe_ratio"] = "Moderate P/E indicates reasonable valuation relative to earnings"
            else:
                interpretation["pe_ratio"] = "High P/E suggests investors expect high growth or the stock may be overvalued"
        
        peg = metrics.get("peg_ratio")
        if peg:
            if peg < 1:
                interpretation["peg_ratio"] = "PEG ratio below 1 suggests the stock may be undervalued relative to growth"
            elif peg < 2:
                interpretation["peg_ratio"] = "PEG ratio between 1-2 indicates reasonable valuation for growth"
            else:
                interpretation["peg_ratio"] = "PEG ratio above 2 suggests the stock may be overvalued relative to growth"
        
        pb = metrics.get("price_to_book")
        if pb:
            if pb < 1:
                interpretation["pb_ratio"] = "Price-to-book below 1 suggests the stock trades below book value"
            elif pb < 3:
                interpretation["pb_ratio"] = "Moderate price-to-book ratio"
            else:
                interpretation["pb_ratio"] = "High price-to-book ratio indicates market values the company significantly above its book value"
        
        return interpretation
    
    async def analyze_financial_health(self, symbol: str) -> Dict[str, Any]:
        """Analyze financial health of a company."""
        metrics = await self.company_data.get_financial_metrics(symbol)
        
        if not metrics.get("available"):
            return metrics
        
        analysis = {
            "symbol": symbol,
            "health_metrics": {
                "profit_margin": metrics.get("profit_margin"),
                "operating_margin": metrics.get("operating_margin"),
                "return_on_assets": metrics.get("return_on_assets"),
                "return_on_equity": metrics.get("return_on_equity"),
                "debt_to_equity": metrics.get("debt_to_equity"),
                "current_ratio": metrics.get("current_ratio"),
                "quick_ratio": metrics.get("quick_ratio"),
                "total_cash": metrics.get("total_cash"),
                "total_debt": metrics.get("total_debt")
            },
            "health_score": self._calculate_health_score(metrics),
            "interpretation": self._interpret_financial_health(metrics),
            "available": True
        }
        
        return analysis
    
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate a simple financial health score (0-100)."""
        score = 50  # Base score
        
        # Profitability adjustments
        profit_margin = metrics.get("profit_margin")
        if profit_margin:
            if profit_margin > 0.2:
                score += 15
            elif profit_margin > 0.1:
                score += 10
            elif profit_margin > 0:
                score += 5
            else:
                score -= 10
        
        # ROE adjustment
        roe = metrics.get("return_on_equity")
        if roe:
            if roe > 0.2:
                score += 15
            elif roe > 0.15:
                score += 10
            elif roe > 0.1:
                score += 5
        
        # Debt adjustment
        debt_to_equity = metrics.get("debt_to_equity")
        if debt_to_equity:
            if debt_to_equity < 0.5:
                score += 10
            elif debt_to_equity < 1:
                score += 5
            elif debt_to_equity > 2:
                score -= 15
        
        # Liquidity adjustment
        current_ratio = metrics.get("current_ratio")
        if current_ratio:
            if current_ratio > 2:
                score += 5
            elif current_ratio < 1:
                score -= 10
        
        return max(0, min(100, score))
    
    def _interpret_financial_health(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Interpret financial health metrics."""
        interpretation = {}
        
        profit_margin = metrics.get("profit_margin")
        if profit_margin:
            if profit_margin > 0.2:
                interpretation["profitability"] = "Strong profit margin indicates efficient operations"
            elif profit_margin > 0.1:
                interpretation["profitability"] = "Moderate profit margin"
            else:
                interpretation["profitability"] = "Low profit margin may indicate competitive pressure or inefficiency"
        
        debt_to_equity = metrics.get("debt_to_equity")
        if debt_to_equity:
            if debt_to_equity < 0.5:
                interpretation["leverage"] = "Low debt-to-equity indicates conservative financial structure"
            elif debt_to_equity < 1:
                interpretation["leverage"] = "Moderate debt-to-equity ratio"
            else:
                interpretation["leverage"] = "High debt-to-equity may indicate higher financial risk"
        
        current_ratio = metrics.get("current_ratio")
        if current_ratio:
            if current_ratio > 1.5:
                interpretation["liquidity"] = "Strong liquidity position with healthy current ratio"
            elif current_ratio > 1:
                interpretation["liquidity"] = "Adequate liquidity"
            else:
                interpretation["liquidity"] = "Low current ratio may indicate short-term liquidity concerns"
        
        return interpretation
    
    async def analyze_growth_trends(self, symbol: str) -> Dict[str, Any]:
        """Analyze growth trends for a company."""
        metrics = await self.company_data.get_financial_metrics(symbol)
        
        if not metrics.get("available"):
            return metrics
        
        analysis = {
            "symbol": symbol,
            "growth_metrics": {
                "revenue_growth": metrics.get("quarterly_revenue_growth"),
                "earnings_growth": metrics.get("earnings_growth"),
                "revenue_estimate_current_year": metrics.get("revenue_estimate_current_year"),
                "revenue_estimate_next_year": metrics.get("revenue_estimate_next_year"),
                "eps_estimate_current_year": metrics.get("eps_estimate_current_year"),
                "eps_estimate_next_year": metrics.get("eps_estimate_next_year")
            },
            "interpretation": self._interpret_growth(metrics),
            "available": True
        }
        
        return analysis
    
    def _interpret_growth(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Interpret growth metrics."""
        interpretation = {}
        
        revenue_growth = metrics.get("quarterly_revenue_growth")
        if revenue_growth:
            if revenue_growth > 0.2:
                interpretation["revenue_growth"] = "Strong quarterly revenue growth indicates business expansion"
            elif revenue_growth > 0.1:
                interpretation["revenue_growth"] = "Moderate revenue growth"
            elif revenue_growth > 0:
                interpretation["revenue_growth"] = "Positive but modest revenue growth"
            else:
                interpretation["revenue_growth"] = "Negative revenue growth may indicate business challenges"
        
        earnings_growth = metrics.get("earnings_growth")
        if earnings_growth:
            if earnings_growth > 0.2:
                interpretation["earnings_growth"] = "Strong earnings growth indicates improving profitability"
            elif earnings_growth > 0.1:
                interpretation["earnings_growth"] = "Moderate earnings growth"
            elif earnings_growth > 0:
                interpretation["earnings_growth"] = "Positive but modest earnings growth"
            else:
                interpretation["earnings_growth"] = "Negative earnings growth may indicate declining profitability"
        
        return interpretation
    
    async def generate_investment_thesis(self, symbol: str) -> Dict[str, Any]:
        """Generate a comprehensive investment thesis."""
        # Gather all relevant data
        overview = await self.company_data.get_company_overview(symbol)
        metrics = await self.company_data.get_financial_metrics(symbol)
        valuation = await self.analyze_valuation(symbol)
        health = await self.analyze_financial_health(symbol)
        growth = await self.analyze_growth_trends(symbol)
        
        thesis = {
            "symbol": symbol,
            "company_overview": overview,
            "financial_health": health,
            "valuation_analysis": valuation,
            "growth_analysis": growth,
            "investment_considerations": self._generate_investment_considerations(
                overview, metrics, valuation, health, growth
            ),
            "key_questions": self._generate_key_questions(overview, metrics),
            "available": all([
                overview.get("available", False),
                metrics.get("available", False)
            ])
        }
        
        return thesis
    
    def _generate_investment_considerations(
        self, 
        overview: Dict, 
        metrics: Dict, 
        valuation: Dict, 
        health: Dict, 
        growth: Dict
    ) -> Dict[str, List[str]]:
        """Generate investment considerations."""
        considerations = {
            "strengths": [],
            "risks": [],
            "opportunities": []
        }
        
        # Strengths
        if health.get("health_score", 0) > 70:
            considerations["strengths"].append("Strong financial health")
        if growth.get("growth_metrics", {}).get("earnings_growth", 0) > 0.15:
            considerations["strengths"].append("Strong earnings growth")
        if metrics.get("profit_margin", 0) > 0.15:
            considerations["strengths"].append("Healthy profit margins")
        
        # Risks
        if metrics.get("debt_to_equity", 0) > 2:
            considerations["risks"].append("High leverage")
        if growth.get("growth_metrics", {}).get("earnings_growth", 0) < 0:
            considerations["risks"].append("Declining earnings")
        if valuation.get("valuation_metrics", {}).get("trailing_pe", 0) > 30:
            considerations["risks"].append("High valuation")
        
        # Opportunities
        if overview.get("overview", {}).get("industry"):
            considerations["opportunities"].append(f"Position in {overview['overview']['industry']} sector")
        if growth.get("growth_metrics", {}).get("revenue_estimate_next_year"):
            considerations["opportunities"].append("Expected revenue growth")
        
        return considerations
    
    def _generate_key_questions(self, overview: Dict, metrics: Dict) -> List[str]:
        """Generate key questions investors should ask."""
        questions = [
            "What are the company's competitive advantages?",
            "What are the main risks to the business model?",
            "How does the company compare to its competitors?",
            "What is the company's growth strategy?",
            "How sustainable are current profit margins?",
            "What are the catalysts for future growth?",
            "How does management allocate capital?",
            "What are the regulatory risks?"
        ]
        
        return questions
