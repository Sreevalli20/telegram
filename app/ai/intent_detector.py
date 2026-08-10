"""Intelligent intent detection system for understanding user requests."""
from typing import Dict, List, Optional, Any
import re
from dataclasses import dataclass


@dataclass
class IntentResult:
    """Result of intent detection."""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    context: Optional[str] = None


class IntentDetector:
    """Detect user intent from natural language messages."""
    
    def __init__(self):
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load intent patterns."""
        return {
            "company_research": [
                {"patterns": [r"tell me about\s+(.+)", r"what is\s+(.+)", r"analyze\s+(.+)", r"research\s+(.+)"], "extract": True},
                {"patterns": [r"(.+)\s+company", r"(.+)\s+overview", r"(.+)\s+business"], "extract": True},
                {"patterns": [r"who is\s+(.+)", r"what does\s+(.+)\s+do"], "extract": True}
            ],
            "stock_lookup": [
                {"patterns": [r"stock price of\s+(.+)", r"price of\s+(.+)", r"current price\s+(.+)"], "extract": True},
                {"patterns": [r"how is\s+(.+)\s+doing", r"what's\s+(.+)\s+trading at"], "extract": True},
                {"patterns": [r"quote\s+(.+)", r"ticker\s+(.+)"], "extract": True},
                {"patterns": [r"analyze\s+(.+)\s+stock", r"(.+)\s+stock"], "extract": True},
                {"patterns": [r"(.+)\s+stock price", r"(.+)\s+quote"], "extract": True}
            ],
            "market_analysis": [
                {"patterns": [r"market update", r"market overview", r"how's the market", r"market today"], "extract": False},
                {"patterns": [r"why did the market", r"market movement", r"market trend"], "extract": False},
                {"patterns": [r"nifty", r"sensex", r"sp 500", r"dow", r"nasdaq"], "extract": False}
            ],
            "comparison": [
                {"patterns": [r"compare\s+(.+)\s+and\s+(.+)", r"(.+)\s+vs\s+(.+)"], "extract": True},
                {"patterns": [r"which is better\s+(.+)\s+or\s+(.+)", r"difference between\s+(.+)\s+and\s+(.+)"], "extract": True}
            ],
            "news_request": [
                {"patterns": [r"news about\s+(.+)", r"latest news\s+(.+)", r"what's new with\s+(.+)"], "extract": True},
                {"patterns": [r"recent news", r"market news", r"financial news"], "extract": False},
                {"patterns": [r"what happened to\s+(.+)", r"what's going on with\s+(.+)"], "extract": True}
            ],
            "document_analysis": [
                {"patterns": [r"analyze this document", r"summarize this pdf", r"read this document"], "extract": False},
                {"patterns": [r"what does this document say", r"explain this report"], "extract": False}
            ],
            "watchlist": [
                {"patterns": [r"track\s+(.+)", r"add\s+(.+)\s+to watchlist", r"watch\s+(.+)"], "extract": True},
                {"patterns": [r"remove\s+(.+)\s+from watchlist", r"untrack\s+(.+)"], "extract": True},
                {"patterns": [r"my watchlist", r"show watchlist", r"tracked stocks"], "extract": False}
            ],
            "alert": [
                {"patterns": [r"alert me if\s+(.+)", r"notify me when\s+(.+)", r"set alert for\s+(.+)"], "extract": True},
                {"patterns": [r"price alert\s+(.+)", r"movement alert\s+(.+)"], "extract": True}
            ],
            "earnings": [
                {"patterns": [r"earnings\s+(.+)", r"(.+)\s+earnings", r"quarterly results\s+(.+)"], "extract": True},
                {"patterns": [r"latest earnings", r"recent earnings report"], "extract": False}
            ],
            "briefing": [
                {"patterns": [r"morning brief", r"daily briefing", r"market summary", r"evening summary"], "extract": False},
                {"patterns": [r"prepare me for", r"brief me on"], "extract": False}
            ],
            "valuation": [
                {"patterns": [r"valuation of\s+(.+)", r"(.+)\s+valuation", r"is\s+(.+)\s+(over|under)valued"], "extract": True},
                {"patterns": [r"pe ratio\s+(.+)", r"price to earnings\s+(.+)"], "extract": True}
            ],
            "financial_health": [
                {"patterns": [r"financial health\s+(.+)", r"(.+)\s+financials", r"balance sheet\s+(.+)"], "extract": True},
                {"patterns": [r"debt\s+(.+)", r"cash\s+(.+)"], "extract": True}
            ],
            "preference_update": [
                {"patterns": [r"i'm interested in\s+(.+)", r"i like\s+(.+)", r"my preference is\s+(.+)"], "extract": True},
                {"patterns": [r"i focus on\s+(.+)", r"i invest in\s+(.+)"], "extract": True}
            ],
            "explanation": [
                {"patterns": [r"what is\s+(.+)", r"explain\s+(.+)", r"what does\s+(.+)mean"], "extract": True},
                {"patterns": [r"how does\s+(.+)work", r"why is\s+(.+)important"], "extract": True},
                {"patterns": [r"(.+)\s+ratio", r"(.+)\s+mean"], "extract": True}
            ],
            "greeting": [
                {"patterns": [r"hello", r"hi", r"hey", r"good morning", r"good afternoon", r"good evening", r"thanks", r"thank you"], "extract": False}
            ],
            "help": [
                {"patterns": [r"help", r"what can you do", r"commands", r"features"], "extract": False}
            ],
            "follow_up": [
                {"patterns": [r"what about", r"tell me more", r"elaborate", r"explain further"], "extract": False},
                {"patterns": [r"and\s+(.+)", r"also\s+(.+)"], "extract": True}
            ]
        }
    
    async def detect(self, message: str, conversation_context: Optional[Dict] = None) -> IntentResult:
        """Detect intent from user message."""
        message_lower = message.lower().strip()
        
        # Check each intent pattern
        for intent, pattern_list in self.patterns.items():
            for pattern_dict in pattern_list:
                for pattern in pattern_dict["patterns"]:
                    match = re.search(pattern, message_lower, re.IGNORECASE)
                    if match:
                        entities = {}
                        if pattern_dict["extract"]:
                            # Extract entities from the match
                            if match.groups():
                                entities["raw_entities"] = list(match.groups())
                                # Try to identify company symbols
                                entities["symbols"] = self._extract_symbols(message)
                                entities["companies"] = self._extract_company_names(message)
                        
                        return IntentResult(
                            intent=intent,
                            confidence=0.85,
                            entities=entities,
                            context=self._build_context(intent, entities, conversation_context)
                        )
        
        # Default to general conversation if no pattern matches
        return IntentResult(
            intent="general",
            confidence=0.5,
            entities={"symbols": self._extract_symbols(message)},
            context="general_conversation"
        )
    
    def _extract_symbols(self, message: str) -> List[str]:
        """Extract stock symbols from message."""
        # Look for uppercase ticker patterns (1-5 letters)
        symbols = re.findall(r'\b[A-Z]{1,5}\b', message)
        # Filter out common words
        common_words = {"THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HAD", "HER", "WAS", "ONE", "OUR", "OUT", "HAS", "HIS", "HOW"}
        symbols = [s for s in symbols if s not in common_words]
        return symbols
    
    def _extract_company_names(self, message: str) -> List[str]:
        """Extract potential company names from message."""
        # This is a simplified extraction
        # In production, use NER or a company name database
        common_companies = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "google": "GOOGL",
            "alphabet": "GOOGL",
            "amazon": "AMZN",
            "tesla": "TSLA",
            "meta": "META",
            "facebook": "META",
            "nvidia": "NVDA",
            "reliance": "RELIANCE.NS",
            "tcs": "TCS.NS",
            "hdfc": "HDFCBANK.NS",
            "infosys": "INFY.NS",
            "icici": "ICICIBANK.NS",
            "sbi": "SBIN.NS",
            "tata": "TCS.NS"
        }
        
        message_lower = message.lower()
        found_companies = []
        
        for name, symbol in common_companies.items():
            if name in message_lower:
                found_companies.append(name)
        
        return found_companies
    
    def _build_context(
        self, 
        intent: str, 
        entities: Dict[str, Any], 
        conversation_context: Optional[Dict] = None
    ) -> str:
        """Build context string for the intent."""
        context_parts = [intent]
        
        if entities.get("symbols"):
            context_parts.append(f"symbols:{','.join(entities['symbols'])}")
        
        if entities.get("companies"):
            context_parts.append(f"companies:{','.join(entities['companies'])}")
        
        if conversation_context:
            if conversation_context.get("last_symbol"):
                context_parts.append(f"last_symbol:{conversation_context['last_symbol']}")
            if conversation_context.get("last_intent"):
                context_parts.append(f"last_intent:{conversation_context['last_intent']}")
        
        return "|".join(context_parts)
    
    async def detect_with_ai(
        self, 
        message: str, 
        ai_provider, 
        conversation_context: Optional[Dict] = None
    ) -> IntentResult:
        """Detect intent using AI for complex queries."""
        # First try pattern matching
        pattern_result = await self.detect(message, conversation_context)
        
        # If pattern matching is confident, use it
        if pattern_result.confidence > 0.8:
            return pattern_result
        
        # Otherwise, use AI for complex intent detection
        intent_prompt = f"""Classify the user's intent into one of these categories:
- company_research: Request for company information or analysis
- stock_lookup: Request for stock price or quote
- market_analysis: Request for market overview or analysis
- comparison: Request to compare companies or stocks
- news_request: Request for news or recent developments
- document_analysis: Request to analyze a document
- watchlist: Request to manage watchlist
- alert: Request to set alerts
- earnings: Request for earnings information
- briefing: Request for market briefing or summary
- valuation: Request for valuation analysis
- financial_health: Request for financial health analysis
- preference_update: User updating their preferences
- explanation: Request to explain a financial concept
- greeting: Greeting or casual conversation
- help: Request for help or information
- follow_up: Follow-up question in conversation
- general: General financial question

User message: {message}

Return only the category name."""
        
        try:
            ai_intent = await ai_provider.generate_response(
                prompt=intent_prompt,
                temperature=0.1
            )
            
            ai_intent = ai_intent.strip().lower()
            
            # Validate AI intent
            valid_intents = list(self.patterns.keys()) + ["general"]
            if ai_intent in valid_intents:
                return IntentResult(
                    intent=ai_intent,
                    confidence=0.75,
                    entities=pattern_result.entities,
                    context=pattern_result.context
                )
        except Exception:
            pass
        
        # Fall back to pattern result
        return pattern_result
