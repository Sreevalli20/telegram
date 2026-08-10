"""Deterministic finance knowledge base - answers common questions without AI."""
from typing import Dict, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DeterministicKnowledge:
    """Deterministic financial knowledge base for common concepts."""
    
    # Finance concept explanations
    CONCEPTS = {
        "pe ratio": """📚 P/E Ratio (Price-to-Earnings Ratio)

The P/E ratio measures a company's current share price relative to its per-share earnings.

Formula: P/E = Stock Price / Earnings Per Share (EPS)

What it tells you:
• High P/E: Investors expect high growth (or stock is overvalued)
• Low P/E: Stock may be undervalued or company is struggling
• Industry comparison is important (tech stocks typically have higher P/E than utilities)

Example:
If a stock trades at $100 and earns $5 per share, P/E = 20
This means investors are willing to pay $20 for every $1 of earnings.

What is a "good" P/E?
There's no universal good P/E. A P/E of 15 might be:
• Good for a high-growth tech company
• High for a utility company
• Low for a cyclical industry

Always compare P/E to:
• Industry averages
• Company's historical P/E
• Growth expectations""",
        
        "price to earnings": """📚 P/E Ratio (Price-to-Earnings Ratio)

The P/E ratio measures a company's current share price relative to its per-share earnings.

Formula: P/E = Stock Price / Earnings Per Share (EPS)

What it tells you:
• High P/E: Investors expect high growth (or stock is overvalued)
• Low P/E: Stock may be undervalued or company is struggling
• Industry comparison is important (tech stocks typically have higher P/E than utilities)

Example:
If a stock trades at $100 and earns $5 per share, P/E = 20
This means investors are willing to pay $20 for every $1 of earnings.""",
        
        "eps": """📚 EPS (Earnings Per Share)

EPS is the portion of a company's profit allocated to each outstanding share of common stock.

Formula: EPS = (Net Income - Preferred Dividends) / Average Outstanding Shares

Types of EPS:
• Basic EPS: Uses actual share count
• Diluted EPS: Accounts for potential share dilution (stock options, convertible securities)

What it tells you:
• Higher EPS generally indicates higher profitability
• Growing EPS over time suggests improving business performance
• Used to calculate P/E ratio

Example:
If a company earns $100M and has 50M shares, EPS = $2.00""",
        
        "earnings per share": """📚 EPS (Earnings Per Share)

EPS is the portion of a company's profit allocated to each outstanding share of common stock.

Formula: EPS = (Net Income - Preferred Dividends) / Average Outstanding Shares

Types of EPS:
• Basic EPS: Uses actual share count
• Diluted EPS: Accounts for potential share dilution (stock options, convertible securities)

What it tells you:
• Higher EPS generally indicates higher profitability
• Growing EPS over time suggests improving business performance
• Used to calculate P/E ratio""",
        
        "dividend": """📚 Dividend

A dividend is a portion of a company's earnings distributed to shareholders, usually quarterly.

Key terms:
• Dividend Yield: Annual dividend / Current stock price
• Ex-Dividend Date: Must own stock before this date to receive dividend
• Payout Ratio: Percentage of earnings paid as dividends
• Declaration Date: When company announces dividend

Example:
If a stock pays $2 annually and trades at $100, the yield is 2%

Dividend types:
• Cash dividends: Most common, paid in cash
• Stock dividends: Paid in additional shares
• Special dividends: One-time payments

Important notes:
• Dividends are not guaranteed - companies can cut them
• High dividend yield may indicate financial distress
• Dividend-paying stocks are often mature, stable companies""",
        
        "dividend yield": """📚 Dividend Yield

Dividend yield measures the annual dividend payment relative to the stock price.

Formula: Dividend Yield = (Annual Dividend / Current Stock Price) × 100%

Example:
If a stock pays $2 annually and trades at $100, the yield is 2%

What it tells you:
• Higher yield = more income per dollar invested
• Extremely high yields may indicate risk (dividend cut likely)
• Compare to industry averages and bond yields

Typical ranges:
• 0-1%: Growth companies (reinvest profits)
• 1-3%: Stable companies (moderate dividends)
• 3-5%: Income-focused companies
• 5%+: High yield (may be risky)""",
        
        "market cap": """📚 Market Capitalization (Market Cap)

The total value of a company's outstanding shares of stock.

Calculation: Market Cap = Share Price × Total Outstanding Shares

Categories:
• Mega-cap: $200B+ (e.g., Apple, Microsoft)
• Large-cap: $10B - $200B
• Mid-cap: $2B - $10B
• Small-cap: $300M - $2B
• Micro-cap: Under $300M

What it tells you:
• Company size and scale
• Market cap affects index inclusion (S&P 500, etc.)
• Larger caps tend to be more stable but slower-growing
• Smaller caps offer higher growth potential but more risk

Important: Market cap indicates company size, not necessarily investment quality.""",
        
        "market capitalization": """📚 Market Capitalization (Market Cap)

The total value of a company's outstanding shares of stock.

Calculation: Market Cap = Share Price × Total Outstanding Shares

Categories:
• Mega-cap: $200B+ (e.g., Apple, Microsoft)
• Large-cap: $10B - $200B
• Mid-cap: $2B - $10B
• Small-cap: $300M - $2B
• Micro-cap: Under $300M

What it tells you:
• Company size and scale
• Market cap affects index inclusion (S&P 500, etc.)
• Larger caps tend to be more stable but slower-growing
• Smaller caps offer higher growth potential but more risk""",
        
        "pb ratio": """📚 P/B Ratio (Price-to-Book Ratio)

P/B ratio compares a company's market value to its book value.

Formula: P/B = Market Price per Share / Book Value per Share

Book Value = Total Assets - Total Liabilities

What it tells you:
• P/B < 1: Stock trading below book value (potentially undervalued)
• P/B > 1: Market values company above its assets
• P/B > 3: May be overvalued or has strong intangible assets

Industry differences:
• Tech companies often have high P/B (intangible assets)
• Banks and industrials often have lower P/B (tangible assets)

Use P/B with:
• P/E ratio
• Return on Equity (ROE)
• Industry comparisons""",
        
        "price to book": """📚 P/B Ratio (Price-to-Book Ratio)

P/B ratio compares a company's market value to its book value.

Formula: P/B = Market Price per Share / Book Value per Share

Book Value = Total Assets - Total Liabilities

What it tells you:
• P/B < 1: Stock trading below book value (potentially undervalued)
• P/B > 1: Market values company above its assets
• P/B > 3: May be overvalued or has strong intangible assets

Industry differences:
• Tech companies often have high P/B (intangible assets)
• Banks and industrials often have lower P/B (tangible assets)""",
        
        "roe": """📚 ROE (Return on Equity)

ROE measures a company's profitability relative to shareholders' equity.

Formula: ROE = (Net Income / Shareholders' Equity) × 100%

What it tells you:
• How efficiently management uses shareholders' money
• Higher ROE generally indicates better efficiency
• Compare to industry averages and company's historical ROE

ROE ranges:
• < 10%: Poor efficiency
• 10-15%: Good efficiency
• 15-20%: Excellent efficiency
• > 20%: Outstanding (but verify sustainability)

Important: High ROE can come from:
• Genuine profitability (good)
• High debt (risky)
• Share buybacks (reduces equity)""",
        
        "return on equity": """📚 ROE (Return on Equity)

ROE measures a company's profitability relative to shareholders' equity.

Formula: ROE = (Net Income / Shareholders' Equity) × 100%

What it tells you:
• How efficiently management uses shareholders' money
• Higher ROE generally indicates better efficiency
• Compare to industry averages and company's historical ROE

ROE ranges:
• < 10%: Poor efficiency
• 10-15%: Good efficiency
• 15-20%: Excellent efficiency
• > 20%: Outstanding (but verify sustainability)""",
        
        "revenue": """📚 Revenue (Top Line)

Revenue is the total income a company earns from its normal business activities.

Types of revenue:
• Operating revenue: From core business operations
• Non-operating revenue: From secondary activities
• Recurring revenue: Predictable, repeated income
• One-time revenue: Single, non-recurring income

What it tells you:
• Company size and market presence
• Business growth (revenue growth rate)
• Market demand for products/services

Revenue vs Profit:
• Revenue = Total money coming in
• Profit = Revenue - Expenses
• A company can have high revenue but low profit""",
        
        "profit": """📚 Profit (Bottom Line)

Profit is what remains after subtracting all expenses from revenue.

Types of profit:
• Gross Profit: Revenue - Cost of Goods Sold
• Operating Profit: Gross Profit - Operating Expenses
• Net Profit: Operating Profit - Interest, Taxes, Other expenses

Profit margins:
• Gross Margin = Gross Profit / Revenue
• Operating Margin = Operating Profit / Revenue
• Net Margin = Net Profit / Revenue

What it tells you:
• Company's financial health
• Efficiency of operations
• Ability to generate returns for shareholders

Important: Consistent, growing profits are better than one-time spikes.""",
        
        "net income": """📚 Net Income

Net income is the company's total profit after all expenses, taxes, and interest.

Formula: Net Income = Revenue - All Expenses (COGS, Operating, Interest, Taxes)

What it tells you:
• The company's actual profitability
• Money available to shareholders (as dividends or retained earnings)
• Used to calculate EPS and ROE

Net income is used for:
• Paying dividends to shareholders
• Reinvesting in the business
• Paying down debt
• Buying back shares

Important: Compare net income across quarters/years to identify trends.""",
        
        "ebitda": """📚 EBITDA (Earnings Before Interest, Taxes, Depreciation, Amortization)

EBITDA measures operating performance excluding capital structure and tax effects.

Formula: EBITDA = Net Income + Interest + Taxes + Depreciation + Amortization

What it tells you:
• Operating profitability independent of financing decisions
• Cash generation ability from operations
• Useful for comparing companies with different tax/debt situations

When to use EBITDA:
• Comparing companies in capital-intensive industries
• Evaluating acquisition targets
• Analyzing companies with different debt levels

When NOT to use EBITDA:
• It ignores capital expenditures (very important for many businesses)
• It doesn't reflect actual cash flow
• Can make unprofitable companies look profitable""",
        
        "free cash flow": """📚 Free Cash Flow (FCF)

FCF is the cash a company generates after accounting for cash outflows to support operations.

Formula: FCF = Operating Cash Flow - Capital Expenditures

What it tells you:
• Cash available for:
  - Paying dividends
  - Buying back shares
  - Paying down debt
  - Making acquisitions
  - Investing in growth

Positive FCF:
• Company generates more cash than it spends
• Generally healthy and sustainable

Negative FCF:
• Company spending more than it generates
• May be investing heavily (good for growth)
• May be struggling (bad if persistent)

FCF vs Net Income:
• FCF is harder to manipulate than accounting earnings
• FCF reflects actual cash generation""",
        
        "debt to equity": """📚 Debt-to-Equity Ratio

D/E ratio compares a company's total debt to its shareholders' equity.

Formula: D/E = Total Liabilities / Total Shareholders' Equity

What it tells you:
• Company's financial leverage
• How much debt is used to finance assets
• Risk level from debt obligations

D/E ranges:
• < 0.5: Conservative (low debt)
• 0.5 - 1.0: Moderate leverage
• 1.0 - 2.0: High leverage
• > 2.0: Very high leverage (risky)

Industry differences:
• Utilities/REITs: Often have higher D/E (stable cash flows)
• Tech/Growth: Often have lower D/E (focus on equity)
• Capital-intensive: Higher D/E common

Important: High debt increases risk but can boost returns in good times.""",
        
        "volatility": """📚 Volatility

Volatility measures how much a stock's price fluctuates over time.

Measurement:
• Standard deviation of returns
• Beta (relative to market)
• Average True Range (ATR)

What it tells you:
• Risk level: Higher volatility = higher risk
• Trading opportunities: More movement = more trading chances
• Investor psychology: Volatility often reflects uncertainty

Volatility ranges:
• Low volatility: < 15% annualized (stable stocks)
• Medium volatility: 15-25% (typical stocks)
• High volatility: 25-40% (growth stocks, small caps)
• Very high volatility: > 40% (speculative stocks)

Beta:
• Beta = 1: Moves with market
• Beta > 1: More volatile than market
• Beta < 1: Less volatile than market

Important: Volatility is not necessarily bad - it creates opportunities.""",
        
        "beta": """📚 Beta

Beta measures a stock's volatility relative to the overall market.

Beta = 1: Stock moves in line with market
Beta > 1: Stock is more volatile than market
Beta < 1: Stock is less volatile than market
Beta = 0: No correlation with market
Negative beta: Moves opposite to market (rare)

Examples:
• Tech stocks: Often beta > 1 (more volatile)
• Utilities: Often beta < 1 (more stable)
• Gold mining: Sometimes negative beta (safe haven)

What it tells you:
• Systematic risk (market risk)
• Expected return relative to market (CAPM)
• Portfolio diversification benefits

Limitations:
• Based on historical data (may not predict future)
• Doesn't capture company-specific risk
• Can change over time""",
        
        "bullish": """📚 Bullish

Bullish refers to optimism that a stock or market will rise in price.

Origin: Bulls attack by thrusting horns upward

Bullish indicators:
• Rising prices with high volume
• Breaking above resistance levels
• Positive economic data
• Strong company earnings
• Favorable analyst ratings

Bullish strategies:
• Going long (buying)
• Call options
• Buying on dips

Bull market characteristics:
• Generally rising prices (20%+ from lows)
• Optimistic investor sentiment
• Strong economic growth
• Low unemployment
• High corporate profits

Remember: Bullish sentiment can be wrong - always do your own research.""",
        
        "bearish": """📚 Bearish

Bearish refers to pessimism that a stock or market will fall in price.

Origin: Bears attack by swiping paws downward

Bearish indicators:
• Falling prices with high volume
• Breaking below support levels
• Negative economic data
• Weak company earnings
• Unfavorable analyst ratings

Bearish strategies:
• Going short (selling)
• Put options
• Selling into rallies

Bear market characteristics:
• Generally falling prices (20%+ from highs)
• Pessimistic investor sentiment
• Economic recession or slowdown
• Rising unemployment
• Declining corporate profits

Remember: Bearish sentiment can be wrong - always do your own research.""",
        
        "support": """📚 Support Level

Support is a price level where a stock tends to find buying interest and stop falling.

How it works:
• At support, demand exceeds supply
• Buyers step in, preventing further decline
• Previous lows often become future support

Types of support:
• Psychological support: Round numbers ($50, $100)
• Trendline support: Connecting higher lows
• Moving average support: 50-day, 200-day lines
• Volume support: Levels with high buying volume

Support becomes resistance:
• Once broken, support often becomes resistance
• Traders who bought at support may sell to break even

Trading at support:
• Buy if support holds with reversal signals
• Sell if support breaks decisively (false breakdown risk)""",
        
        "resistance": """📚 Resistance Level

Resistance is a price level where a stock tends to find selling pressure and stop rising.

How it works:
• At resistance, supply exceeds demand
• Sellers step in, preventing further advance
• Previous highs often become future resistance

Types of resistance:
• Psychological resistance: Round numbers ($50, $100)
• Trendline resistance: Connecting lower highs
• Moving average resistance: 50-day, 200-day lines
• Volume resistance: Levels with high selling volume

Resistance becomes support:
• Once broken, resistance often becomes support
• Short sellers may cover, creating buying pressure

Trading at resistance:
• Sell if resistance holds with reversal signals
• Buy if resistance breaks decisively (breakout)""",
        
        "moving average": """📚 Moving Average (MA)

Moving average smooths price data to create a single flowing line, reducing noise.

Common types:
• Simple Moving Average (SMA): Equal weight to all data points
• Exponential Moving Average (EMA): More weight to recent data

Common periods:
• 20-day: Short-term trend
• 50-day: Medium-term trend
• 200-day: Long-term trend (widely watched)

How to use:
• Price above MA = bullish trend
• Price below MA = bearish trend
• MA crossovers: Golden cross (50 above 200) = bullish
• MA as support/resistance

Example:
If 50-day MA is $100 and price is $105, short-term trend is up

Limitations:
• Lagging indicator (based on past data)
• Can give false signals in choppy markets
• Works best in trending markets""",
        
        "cagr": """📚 CAGR (Compound Annual Growth Rate)

CAGR measures the mean annual growth rate of an investment over a specified period.

Formula: CAGR = (Ending Value / Beginning Value)^(1/n) - 1

Where n = number of years

Example:
If $10,000 grows to $16,105 in 5 years:
CAGR = (16,105 / 10,000)^(1/5) - 1 = 10% annually

What it tells you:
• Smooth annual growth rate
• Allows comparison between different investments
• Accounts for compounding effect

Uses:
• Comparing investment performance
• Projecting future values
• Evaluating business growth

Important: CAGR assumes smooth growth, which rarely happens in reality.""",
        
        "inflation": """📚 Inflation

Inflation is the rate at which prices for goods and services rise over time.

Measurement:
• CPI (Consumer Price Index): Most common measure
• PPI (Producer Price Index): Wholesale prices
• Core inflation: Excludes food and energy (more stable)

Impact on investments:
• Stocks: Can benefit if companies raise prices
• Bonds: Hurt by inflation (fixed payments lose value)
• Real estate: Often hedge against inflation
• Cash: Loses purchasing power

Central bank response:
• High inflation → Higher interest rates → Slower economy
• Low inflation → Lower interest rates → Stimulates economy

Investor strategies:
• During high inflation: TIPS, commodities, real estate
• During low inflation: Growth stocks, bonds

Historical average: ~2-3% annually in developed economies""",
        
        "interest rates": """📚 Interest Rates

Interest rates are the cost of borrowing money or the return on lending money.

Types:
• Federal Funds Rate: Set by central bank (US Federal Reserve)
• Prime Rate: Rate banks charge their best customers
• Mortgage Rate: Rate for home loans
• Bond Yield: Return on government/corporate bonds

Impact on markets:
• Higher rates → Bad for stocks (higher borrowing costs)
• Higher rates → Bad for bonds (bond prices fall)
• Lower rates → Good for stocks (cheaper to borrow)
• Lower rates → Good for bonds (bond prices rise)

Rate changes affect:
• Tech/growth stocks (most sensitive to rates)
• Financial stocks (benefit from higher rates)
• Real estate (sensitive to mortgage rates)
• Consumer spending (affected by loan costs)

Investor strategies:
• Expecting rate hikes: Rotate to value stocks, shorten bond duration
• Expecting rate cuts: Rotate to growth stocks, lengthen bond duration""",
        
        "bonds": """📚 Bonds

Bonds are debt securities where investors lend money to entities in exchange for periodic interest.

Key terms:
• Coupon: Interest payment (usually semi-annual)
• Maturity: When principal is repaid
• Yield: Annual return (coupon / price)
• Face value: Principal amount repaid at maturity

Bond types:
• Government bonds: Lowest risk (US Treasuries)
• Corporate bonds: Higher risk, higher yield
• Municipal bonds: Tax-exempt (for local projects)
• Junk bonds: High risk, high yield

Bond prices and yields:
• Inverse relationship: Price up = Yield down
• Interest rate risk: Rates up = Bond prices down

When to buy bonds:
• Seeking income
• Diversifying portfolio
• Reducing portfolio risk
• Expecting falling interest rates""",
        
        "etf": """📚 ETF (Exchange-Traded Fund)

ETF is a basket of securities that trades on an exchange like a single stock.

Key features:
• Diversification: Own many securities in one fund
• Liquidity: Trade throughout the day like stocks
• Lower fees: Generally cheaper than mutual funds
• Transparency: Holdings disclosed daily

Common ETF types:
• Index ETFs: Track market indices (SPY tracks S&P 500)
• Sector ETFs: Focus on specific industries (XLK = tech)
• International ETFs: Foreign market exposure
• Commodity ETFs: Gold, oil, etc.
• Bond ETFs: Fixed income exposure

Advantages vs mutual funds:
• Trade anytime (not just end of day)
• Generally lower expense ratios
• More tax-efficient
• No minimum investment

Popular examples:
• SPY: S&P 500
• QQQ: Nasdaq 100
• IWM: Russell 2000 (small caps)
• VTI: Total US stock market""",
        
        "index": """📚 Market Index

A market index measures the performance of a group of stocks representing a market or sector.

Major US indices:
• S&P 500: 500 large US companies (most widely followed)
• Dow Jones: 30 large US companies (price-weighted)
• Nasdaq Composite: Tech-heavy, over 3,000 companies
• Russell 2000: 2,000 small-cap companies

International indices:
• FTSE 100: UK large caps
• DAX: German large caps
• Nikkei 225: Japanese large caps
• Hang Seng: Hong Kong large caps

Sector indices:
• Technology, Healthcare, Financial, Energy, etc.

How indices are used:
• Benchmark for performance comparison
• Economic indicators
• Basis for index funds and ETFs
• Market sentiment gauges

Investing in indices:
• Index funds/ETFs offer broad diversification
• Low-cost way to invest in entire markets
• Generally outperform most active managers long-term"""
    }
    
    @classmethod
    def get_concept_explanation(cls, concept: str) -> Optional[str]:
        """Get explanation for a finance concept."""
        if not concept:
            return None
        
        concept_lower = concept.lower().strip()
        
        # Direct match
        if concept_lower in cls.CONCEPTS:
            return cls.CONCEPTS[concept_lower]
        
        # Partial match
        for key, explanation in cls.CONCEPTS.items():
            if concept_lower in key or key in concept_lower:
                return explanation
        
        return None
    
    @classmethod
    def has_concept(cls, message: str) -> bool:
        """Check if message asks about a known finance concept."""
        message_lower = message.lower()
        
        # Check for explanation keywords
        explanation_keywords = ["what is", "explain", "what does", "meaning of", "define"]
        has_explanation_keyword = any(keyword in message_lower for keyword in explanation_keywords)
        
        if not has_explanation_keyword:
            return False
        
        # Check if message contains known concepts
        for concept in cls.CONCEPTS.keys():
            if concept in message_lower:
                return True
        
        return False
    
    @classmethod
    def extract_concept(cls, message: str) -> Optional[str]:
        """Extract the finance concept from a message."""
        message_lower = message.lower()
        
        for concept in cls.CONCEPTS.keys():
            if concept in message_lower:
                return concept
        
        return None