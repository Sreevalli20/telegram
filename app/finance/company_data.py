"""Company data service for fetching comprehensive company information."""
import yfinance as yf
from typing import Dict, List, Optional, Any
from datetime import datetime


class CompanyDataService:
    """Service for fetching company data and information."""
    
    def __init__(self):
        self.cache = {}
    
    async def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive company overview."""
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            
            return {
                "symbol": symbol.upper(),
                "company_name": info.get('longName') or info.get('shortName'),
                "industry": info.get('industry'),
                "sector": info.get('sector'),
                "business_summary": info.get('longBusinessSummary'),
                "website": info.get('website'),
                "employees": info.get('fullTimeEmployees'),
                "headquarters": {
                    "city": info.get('city'),
                    "state": info.get('state'),
                    "country": info.get('country')
                },
                "founded": info.get('companyOfficers', [{}])[0].get('age') if info.get('companyOfficers') else None,
                "available": True
            }
        except Exception as e:
            return {
                "symbol": symbol.upper(),
                "error": str(e),
                "available": False
            }
    
    async def get_financial_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get key financial metrics."""
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            
            return {
                "symbol": symbol.upper(),
                "market_cap": info.get('marketCap'),
                "enterprise_value": info.get('enterpriseValue'),
                "trailing_pe": info.get('trailingPE'),
                "forward_pe": info.get('forwardPE'),
                "peg_ratio": info.get('pegRatio'),
                "price_to_book": info.get('priceToBook'),
                "price_to_sales": info.get('priceToSalesTrailing12Months'),
                "enterprise_to_ebitda": info.get('enterpriseToEbitda'),
                "profit_margin": info.get('profitMargins'),
                "operating_margin": info.get('operatingMargins'),
                "return_on_assets": info.get('returnOnAssets'),
                "return_on_equity": info.get('returnOnEquity'),
                "revenue_per_share": info.get('revenuePerShare'),
                "quarterly_revenue_growth": info.get('revenueQuarterlyGrowth'),
                "earnings_growth": info.get('earningsGrowth'),
                "debt_to_equity": info.get('debtToEquity'),
                "current_ratio": info.get('currentRatio'),
                "quick_ratio": info.get('quickRatio'),
                "total_cash": info.get('totalCash'),
                "total_debt": info.get('totalDebt'),
                "total_revenue": info.get('totalRevenue'),
                "gross_profit": info.get('grossProfits'),
                "ebitda": info.get('ebitda'),
                "free_cashflow": info.get('freeCashflow'),
                "operating_cashflow": info.get('operatingCashflow'),
                "available": True
            }
        except Exception as e:
            return {
                "symbol": symbol.upper(),
                "error": str(e),
                "available": False
            }
    
    async def get_company_leadership(self, symbol: str) -> List[Dict[str, Any]]:
        """Get company leadership information."""
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            
            officers = info.get('companyOfficers', [])
            leadership = []
            
            for officer in officers[:10]:  # Top 10 officers
                leadership.append({
                    "name": officer.get('name'),
                    "title": officer.get('title'),
                    "age": officer.get('age'),
                    "total_pay": officer.get('totalPay'),
                    "exercised_value": officer.get('exercisedValue'),
                    "year_born": officer.get('yearBorn')
                })
            
            return leadership
        except Exception as e:
            return []
    
    async def get_competitors(self, symbol: str) -> List[Dict[str, str]]:
        """Get company competitors."""
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            
            # yfinance doesn't directly provide competitors
            # This is a simplified mapping for common companies
            competitor_map = {
                "AAPL": ["MSFT", "GOOGL", "AMZN", "META"],
                "MSFT": ["AAPL", "GOOGL", "AMZN", "ORCL"],
                "GOOGL": ["MSFT", "META", "AAPL", "AMZN"],
                "AMZN": ["WMT", "GOOGL", "MSFT", "META"],
                "TSLA": ["F", "GM", "RIVN", "LCID"],
                "META": ["GOOGL", "SNAP", "PINS", "TWTR"],
                "NVDA": ["AMD", "INTC", "QCOM", "MRVL"],
                "RELIANCE.NS": ["TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"],
                "TCS.NS": ["INFY.NS", "HCLTECH.NS", "WIPRO.NS", "LTIM.NS"],
                "HDFCBANK.NS": ["ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"]
            }
            
            competitors = competitor_map.get(symbol.upper(), [])
            
            return [{"symbol": comp} for comp in competitors]
        except Exception as e:
            return []
    
    async def get_earnings_data(self, symbol: str) -> Dict[str, Any]:
        """Get earnings data."""
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            
            return {
                "symbol": symbol.upper(),
                "earnings_date": info.get('nextEarningsDate'),
                "eps_current": info.get('trailingEps'),
                "eps_forward": info.get('forwardEps'),
                "eps_estimate_current_year": info.get('currentYearEarningsEstimate'),
                "eps_estimate_next_year": info.get('nextYearEarningsEstimate'),
                "revenue_estimate_current_year": info.get('currentYearRevenueEstimate'),
                "revenue_estimate_next_year": info.get('nextYearRevenueEstimate'),
                "available": True
            }
        except Exception as e:
            return {
                "symbol": symbol.upper(),
                "error": str(e),
                "available": False
            }
    
    async def get_dividend_info(self, symbol: str) -> Dict[str, Any]:
        """Get dividend information."""
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            
            return {
                "symbol": symbol.upper(),
                "dividend_rate": info.get('dividendRate'),
                "dividend_yield": info.get('dividendYield'),
                "payout_ratio": info.get('payoutRatio'),
                "ex_dividend_date": info.get('exDividendDate'),
                "last_dividend_date": info.get('lastDividendDate'),
                "five_year_avg_dividend_yield": info.get('fiveYearAvgDividendYield'),
                "available": True
            }
        except Exception as e:
            return {
                "symbol": symbol.upper(),
                "error": str(e),
                "available": False
            }
    
    async def get_company_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent company news."""
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
                    "published": item.get('providerPublishTime'),
                    "source": item.get('publisher'),
                    "summary": item.get('summary')
                })
            
            return news_items
        except Exception as e:
            return []
    
    async def get_complete_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Get complete company profile combining all data."""
        overview = await self.get_company_overview(symbol)
        metrics = await self.get_financial_metrics(symbol)
        leadership = await self.get_company_leadership(symbol)
        competitors = await self.get_competitors(symbol)
        earnings = await self.get_earnings_data(symbol)
        dividends = await self.get_dividend_info(symbol)
        
        return {
            "overview": overview,
            "financial_metrics": metrics,
            "leadership": leadership,
            "competitors": competitors,
            "earnings": earnings,
            "dividends": dividends,
            "last_updated": datetime.now().isoformat()
        }
