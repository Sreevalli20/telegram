"""Financial explanation service for explaining concepts in user-friendly terms."""
from typing import Dict, Any, Optional
from app.ai.providers import BaseAIProvider


class ExplanationService:
    """Service for explaining financial concepts clearly and effectively."""
    
    def __init__(self, ai_provider: Optional[BaseAIProvider] = None):
        self.ai_provider = ai_provider
        self.common_concepts = self._load_common_concepts()
    
    def _load_common_concepts(self) -> Dict[str, str]:
        """Load common financial concepts and their explanations."""
        return {
            "pe_ratio": "P/E Ratio (Price-to-Earnings) measures how much investors are willing to pay for each dollar of a company's earnings. A high P/E suggests investors expect high growth, while a low P/E may indicate the stock is undervalued or the company has low growth expectations.",
            "eps": "EPS (Earnings Per Share) is the portion of a company's profit allocated to each outstanding share of stock. It's a key indicator of a company's profitability.",
            "market_cap": "Market Capitalization is the total value of a company's outstanding shares. It's calculated by multiplying the current stock price by the total number of shares.",
            "dividend_yield": "Dividend Yield is the annual dividend payment divided by the stock's current price, expressed as a percentage. It shows the return on investment from dividends alone.",
            "beta": "Beta measures a stock's volatility relative to the overall market. A beta above 1 means the stock is more volatile than the market, while below 1 means it's less volatile.",
            "roe": "ROE (Return on Equity) measures a company's profitability by revealing how much profit a company generates with the money shareholders have invested.",
            "debt_to_equity": "Debt-to-Equity Ratio compares a company's total debt to its shareholders' equity. It indicates the proportion of equity and debt used to finance the company's assets.",
            "ebitda": "EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization) measures a company's operating performance. It's often used to compare profitability between companies.",
            "free_cash_flow": "Free Cash Flow represents the cash a company generates after accounting for cash outflows to support operations and maintain its capital assets.",
            "volatility": "Volatility measures how much a stock's price fluctuates. High volatility means the price can change dramatically in a short period, which indicates higher risk but potentially higher returns.",
            "support_level": "Support Level is a price point where a stock tends to find buying interest, preventing it from falling further. It's like a floor for the stock price.",
            "resistance_level": "Resistance Level is a price point where a stock tends to find selling pressure, preventing it from rising further. It's like a ceiling for the stock price.",
            "moving_average": "Moving Average smooths out price data by creating a constantly updated average price. It helps identify trends by filtering out the noise from random price fluctuations.",
            "rsi": "RSI (Relative Strength Index) measures the speed and change of price movements. It ranges from 0 to 100, with readings above 70 indicating overbought conditions and below 30 indicating oversold conditions.",
            "volume": "Volume is the number of shares traded during a given period. High volume indicates strong investor interest and can confirm the strength of a price movement.",
            "margin_call": "A Margin Call occurs when an investor's account value falls below the broker's required minimum. The broker demands the investor deposit additional funds or securities to bring the account back to the required level.",
            "short_selling": "Short Selling is selling borrowed shares with the intention of buying them back later at a lower price. It's a bet that the stock price will decline.",
            "options": "Options are financial derivatives that give buyers the right, but not the obligation, to buy or sell an underlying asset at a predetermined price and date.",
            "etf": "ETF (Exchange-Traded Fund) is a basket of securities that trades on an exchange like a stock. It offers diversification and typically lower fees than mutual funds.",
            "index": "An Index is a benchmark that tracks a group of stocks representing a specific market or sector. Examples include the S&P 500 (US large-cap stocks) and Nifty 50 (Indian large-cap stocks)."
        }
    
    async def explain_concept(
        self,
        concept: str,
        user_experience_level: Optional[str] = "intermediate"
    ) -> Dict[str, Any]:
        """Explain a financial concept in user-friendly terms."""
        # Check if we have a pre-defined explanation
        concept_lower = concept.lower().replace(" ", "_").replace("-", "_")
        
        if concept_lower in self.common_concepts:
            base_explanation = self.common_concepts[concept_lower]
        else:
            # Generate explanation using AI
            base_explanation = await self._generate_concept_explanation(concept, user_experience_level)
        
        # Enhance with context and examples
        enhanced_explanation = await self._enhance_explanation(
            concept,
            base_explanation,
            user_experience_level
        )
        
        return {
            "concept": concept,
            "explanation": enhanced_explanation,
            "experience_level": user_experience_level,
            "available": True
        }
    
    async def _generate_concept_explanation(
        self,
        concept: str,
        experience_level: str
    ) -> str:
        """Generate explanation for unknown concepts using AI."""
        level_guidance = {
            "beginner": "Explain in simple terms with everyday analogies. Avoid jargon.",
            "intermediate": "Explain with some technical details but keep it accessible.",
            "advanced": "Provide detailed technical explanation with nuances."
        }
        
        guidance = level_guidance.get(experience_level, level_guidance["intermediate"])
        
        prompt = f"""Explain the financial concept: {concept}

{guidance}

Include:
1. What it is (simple definition)
2. Why it matters to investors
3. How it's used in practice
4. A simple example

Be concise and clear."""
        
        explanation = await self.ai_provider.generate_response(
            prompt=prompt,
            temperature=0.5
        )
        
        return explanation
    
    async def _enhance_explanation(
        self,
        concept: str,
        base_explanation: str,
        experience_level: str
    ) -> str:
        """Enhance explanation with context and practical examples."""
        enhancement_prompt = f"""Enhance this explanation of {concept}:

Base explanation: {base_explanation}

Add:
1. Why investors should care about this
2. Real-world impact on investment decisions
3. Common misconceptions to avoid
4. When this concept is most useful

Keep the tone professional but accessible. Target audience: {experience_level} level investor."""
        
        enhanced = await self.ai_provider.generate_response(
            prompt=enhancement_prompt,
            temperature=0.5
        )
        
        return enhanced
    
    async def explain_metric(
        self,
        metric_name: str,
        metric_value: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Explain a specific financial metric value in context."""
        context_str = ""
        if context:
            context_str = f"\nContext: {context}"
        
        prompt = f"""Explain this financial metric:

Metric: {metric_name}
Value: {metric_value}
{context_str}

Explain:
1. What this value means in plain English
2. Whether this value is good, bad, or neutral
3. What it suggests about the company/investment
4. What investors should watch for

Be specific and actionable."""
        
        explanation = await self.ai_provider.generate_response(
            prompt=prompt,
            temperature=0.5
        )
        
        return explanation
    
    async def explain_market_event(
        self,
        event_description: str,
        impact_analysis: Optional[str] = None
    ) -> str:
        """Explain a market event and its implications."""
        impact_str = f"\nImpact Analysis: {impact_analysis}" if impact_analysis else ""
        
        prompt = f"""Explain this market event:

Event: {event_description}
{impact_str}

Explain:
1. What happened in simple terms
2. Why it matters to investors
3. Which sectors or types of investments are most affected
4. What investors should consider doing

Be clear and focus on actionable insights."""
        
        explanation = await self.ai_provider.generate_response(
            prompt=prompt,
            temperature=0.5
        )
        
        return explanation
    
    def get_available_concepts(self) -> list:
        """Get list of available financial concepts."""
        return sorted(self.common_concepts.keys())
