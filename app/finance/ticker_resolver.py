"""Centralized company/ticker resolution layer with robust validation."""
from typing import Optional, Dict, List
import re
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TickerResolver:
    """Centralized resolver for company names to stock tickers with validation."""
    
    # Common company name to ticker mappings
    COMPANY_TO_TICKER = {
        # US Tech
        "apple": "AAPL",
        "microsoft": "MSFT",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "amazon": "AMZN",
        "tesla": "TSLA",
        "meta": "META",
        "facebook": "META",
        "nvidia": "NVDA",
        "netflix": "NFLX",
        "adobe": "ADBE",
        "salesforce": "CRM",
        "oracle": "ORCL",
        "intel": "INTC",
        "amd": "AMD",
        "qualcomm": "QCOM",
        "ibm": "IBM",
        "cisco": "CSCO",
        
        # US Finance
        "jpmorgan": "JPM",
        "jpmorgan chase": "JPM",
        "bank of america": "BAC",
        "wells fargo": "WFC",
        "goldman sachs": "GS",
        "morgan stanley": "MS",
        "citigroup": "C",
        "blackrock": "BLK",
        "visa": "V",
        "mastercard": "MA",
        
        # US Consumer/Other
        "walmart": "WMT",
        "costco": "COST",
        "home depot": "HD",
        "mcdonalds": "MCD",
        "starbucks": "SBUX",
        "nike": "NKE",
        "disney": "DIS",
        "comcast": "CMCSA",
        "coca-cola": "KO",
        "pepsi": "PEP",
        "johnson & johnson": "JNJ",
        "procter & gamble": "PG",
        
        # Indian Stocks
        "reliance": "RELIANCE.NS",
        "tcs": "TCS.NS",
        "tata consultancy services": "TCS.NS",
        "hdfc": "HDFCBANK.NS",
        "hdfc bank": "HDFCBANK.NS",
        "infosys": "INFY.NS",
        "icici": "ICICIBANK.NS",
        "icici bank": "ICICIBANK.NS",
        "sbi": "SBIN.NS",
        "state bank of india": "SBIN.NS",
        "bharti airtel": "BHARTIARTL.NS",
        "airtel": "BHARTIARTL.NS",
        "itc": "ITC.NS",
        "kotak": "KOTAKBANK.NS",
        "kotak bank": "KOTAKBANK.NS",
        "tata motors": "TATAMOTORS.NS",
        "tata steel": "TATASTEEL.NS",
        "hindustan unilever": "HINDUNILVR.NS",
        "hindustan unilever": "HINDUNILVR.NS",
        "axis bank": "AXISBANK.NS",
        "lic": "LICI.NS",
    }
    
    # Valid ticker pattern
    TICKER_PATTERN = re.compile(r'^[A-Z]{1,5}(\.[A-Z]{1,3})?$')
    
    # English stop words that should never be tickers
    STOP_WORDS = {
        "A", "AN", "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", 
        "CAN", "HAD", "HER", "WAS", "ONE", "OUR", "OUT", "HAS", "HIS", "HOW",
        "IS", "IT", "ME", "MY", "WE", "WHAT", "DO", "SO", "GO", "NO", "UP", "ON",
        "IN", "AT", "TO", "BY", "OF", "OR", "IF", "AS", "BE", "HE", "WE", "OR",
        "THIS", "THAT", "THESE", "THOSE", "AM", "BEEN", "BEING", "HAVE", "HAS",
        "HAD", "DO", "DOES", "DID", "WILL", "WOULD", "SHOULD", "COULD", "MAY",
        "MIGHT", "MUST", "SHALL", "STOCK", "COMPANY", "PRICE", "MARKET", "SHARE",
        "I", "ANALYZE", "TELL", "ABOUT", "WHAT", "IS", "ARE", "WHY", "HOW", "WHEN"
    }
    
    @classmethod
    def resolve(cls, input_text: str) -> Optional[str]:
        """
        Resolve input text to a valid ticker symbol.
        
        Args:
            input_text: Company name, ticker, or partial name
            
        Returns:
            Valid ticker symbol or None if cannot be resolved
        """
        if not input_text:
            return None
        
        input_text = input_text.strip()
        input_lower = input_text.lower()
        
        # Check if it's already a valid ticker format
        if cls._is_valid_ticker_format(input_text):
            ticker = input_text.upper()
            # Validate it's not a stop word
            if ticker not in cls.STOP_WORDS:
                logger.info(f"Resolved '{input_text}' to ticker '{ticker}' (direct)")
                return ticker
            else:
                logger.warning(f"Rejected ticker '{ticker}' as it's a stop word")
                return None
        
        # Try company name mapping
        for company_name, ticker in cls.COMPANY_TO_TICKER.items():
            if company_name in input_lower or input_lower in company_name:
                logger.info(f"Resolved '{input_text}' to ticker '{ticker}' (company name)")
                return ticker
        
        # Try partial matches
        for company_name, ticker in cls.COMPANY_TO_TICKER.items():
            if input_lower in company_name:
                logger.info(f"Resolved '{input_text}' to ticker '{ticker}' (partial match)")
                return ticker
        
        logger.warning(f"Could not resolve '{input_text}' to any known ticker")
        return None
    
    @classmethod
    def _is_valid_ticker_format(cls, text: str) -> bool:
        """Check if text matches valid ticker format."""
        # Allow 1-5 uppercase letters, optional .NS, .TO, etc
        return bool(cls.TICKER_PATTERN.match(text.upper()))
    
    @classmethod
    def extract_and_resolve(cls, message: str) -> List[str]:
        """
        Extract potential tickers from message and resolve them.
        
        Args:
            message: User message text
            
        Returns:
            List of resolved ticker symbols
        """
        resolved = []
        
        # Extract uppercase patterns that look like tickers
        potential_tickers = re.findall(r'\b[A-Z]{1,5}(\.[A-Z]{1,3})?\b', message)
        
        for ticker in potential_tickers:
            if ticker not in cls.STOP_WORDS:
                resolved.append(ticker)
        
        # Try to resolve company names
        message_lower = message.lower()
        for company_name, ticker in cls.COMPANY_TO_TICKER.items():
            if company_name in message_lower:
                if ticker not in resolved:
                    resolved.append(ticker)
        
        logger.info(f"Extracted and resolved tickers from message: {resolved}")
        return resolved
    
    @classmethod
    def requires_symbol(cls, intent: str, entities: Dict) -> bool:
        """
        Check if an intent requires a symbol but doesn't have one.
        
        Args:
            intent: Detected intent
            entities: Extracted entities
            
        Returns:
            True if symbol is required but missing
        """
        symbol_required_intents = [
            "stock_analysis", "stock_lookup", "company_research", 
            "valuation", "financial_health", "comparison"
        ]
        
        if intent in symbol_required_intents:
            symbols = entities.get("symbols", [])
            companies = entities.get("companies", [])
            
            # If we have neither symbols nor companies, symbol is required but missing
            if not symbols and not companies:
                return True
        
        return False