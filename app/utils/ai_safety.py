"""AI safety utilities for financial responses."""

import re
from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Unsafe phrases that should be avoided in financial responses
UNSAFE_PHRASES = [
    "guarantee",
    "guaranteed",
    "certain",
    "definitely",
    "without a doubt",
    "will make",
    "will earn",
    "will profit",
    "sure thing",
    "can't lose",
    "risk-free",
    "foolproof",
    "guaranteed return",
    "guaranteed profit",
    "financial advice",
    "investment advice",
    "recommend you buy",
    "recommend you sell",
    "you should invest",
    "you should purchase",
    "you should sell",
    "best investment",
    "perfect investment",
    "must buy",
    "must sell",
]

# Safe phrases that should be encouraged
SAFE_PHRASES = [
    "based on available information",
    "key factors to consider",
    "please perform your own research",
    "this is not financial advice",
    "for informational purposes only",
    "potential risks",
    "consider your risk tolerance",
    "consult with a financial advisor",
    "past performance does not guarantee",
    "historical data suggests",
    "according to the data",
    "the analysis indicates",
    "it appears that",
    "may be worth considering",
    "could be an opportunity",
    "potential upside",
    "potential downside",
]


def contains_unsafe_language(text: str) -> tuple[bool, list[str]]:
    """
    Check if text contains unsafe financial language.
    
    Args:
        text: The text to check
        
    Returns:
        tuple: (contains_unsafe, list_of_unsafe_phrases)
    """
    text_lower = text.lower()
    found_unsafe = []
    
    for phrase in UNSAFE_PHRASES:
        if phrase in text_lower:
            found_unsafe.append(phrase)
    
    return len(found_unsafe) > 0, found_unsafe


def add_safety_disclaimer(text: str) -> str:
    """
    Add safety disclaimer to financial responses.
    
    Args:
        text: The original response
        
    Returns:
        str: Response with safety disclaimer
    """
    disclaimer = "\n\n⚠️ **Disclaimer**: This analysis is for informational purposes only and does not constitute financial advice. Please perform your own research and consult with a qualified financial advisor before making investment decisions."
    
    # Don't add if already present
    if "disclaimer" in text.lower() or "financial advice" in text.lower():
        return text
    
    return text + disclaimer


def soften_language(text: str) -> str:
    """
    Soften absolute language to be more tentative and safe.
    
    Args:
        text: The original text
        
    Returns:
        str: Text with softened language
    """
    replacements = {
        "will ": "may ",
        "will definitely ": "may potentially ",
        "guaranteed ": "potentially ",
        "certain ": "likely ",
        "without a doubt ": "it appears ",
        "must ": "might ",
        "should ": "could ",
        "best ": "potentially strong ",
        "perfect ": "potentially suitable ",
    }
    
    for old, new in replacements.items():
        text = re.sub(rf'\b{re.escape(old)}', new, text, flags=re.IGNORECASE)
    
    return text


def validate_financial_response(response: str) -> tuple[bool, str, Optional[str]]:
    """
    Validate a financial response for safety.
    
    Args:
        response: The AI response to validate
        
    Returns:
        tuple: (is_safe, safe_response, warning_message)
    """
    # Check for unsafe language
    has_unsafe, unsafe_phrases = contains_unsafe_language(response)
    
    if has_unsafe:
        logger.warning(f"Unsafe language detected in response: {unsafe_phrases}")
        # Soften the language
        response = soften_language(response)
    
    # Ensure safety disclaimer is present
    response = add_safety_disclaimer(response)
    
    # Check if response is too short (might indicate an error)
    if len(response) < 50:
        return False, response, "Response appears to be incomplete or too short"
    
    return True, response, None


def get_safety_context() -> str:
    """
    Get safety context to include in AI prompts.
    
    Returns:
        str: Safety context string
    """
    return """
IMPORTANT SAFETY GUIDELINES:
- Never guarantee returns or profits
- Never provide definitive financial advice
- Always use tentative language (e.g., "may", "could", "appears to")
- Always mention that this is for informational purposes only
- Always encourage users to do their own research
- Always mention potential risks
- Never claim certainty about future performance
- Avoid phrases like "guaranteed", "certain", "definitely", "must", "should"
- Use phrases like "based on available information", "key factors to consider", "data suggests"
- Remind users to consult with a qualified financial advisor
"""


def sanitize_stock_symbol(symbol: str) -> str:
    """
    Sanitize and validate stock symbol input.
    
    Args:
        symbol: The stock symbol to sanitize
        
    Returns:
        str: Sanitized symbol
    """
    # Remove whitespace and convert to uppercase
    symbol = symbol.strip().upper()
    
    # Remove common suffixes that might be confused
    suffixes_to_remove = ["STOCK", "SHARES", "CORP", "INC", "LTD"]
    for suffix in suffixes_to_remove:
        if symbol.endswith(suffix):
            symbol = symbol[:-len(suffix)]
    
    return symbol
