from typing import Optional, List, Dict, Any
from app.ai.providers import BaseAIProvider
from app.ai.intent_detector import IntentDetector


class ConversationAgent:
    """Agent for handling conversational interactions with context awareness and follow-up intelligence."""
    
    def __init__(self, ai_provider: Optional[BaseAIProvider] = None):
        self.ai_provider = ai_provider
        self.intent_detector = IntentDetector()
        self.conversation_history = {}  # Store conversation history per user
    
    async def process_message(
        self,
        user_message: str,
        conversation_history: List[dict],
        user_context: Optional[dict] = None
    ) -> str:
        """Process a user message with conversation context."""
        # Build system prompt with user context
        system_prompt = self._build_system_prompt(user_context)
        
        # Prepare messages for AI
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-20:])  # Last 20 messages for context
        messages.append({"role": "user", "content": user_message})
        
        # Generate response
        response = await self.ai_provider.chat_completion(
            messages=messages,
            temperature=0.7
        )
        
        return response
    
    def _build_system_prompt(self, user_context: Optional[dict]) -> str:
        """Build system prompt based on user context."""
        base_prompt = """You are ATLAS, an AI-powered Financial Assistant. You provide professional financial analysis and insights.

Key principles:
- Be concise and direct
- Ask clarifying questions when requests are ambiguous
- Avoid hallucinations - only provide information you're confident about
- Explain your reasoning when making financial recommendations
- Maintain a professional yet conversational tone
- Remember previous context in the conversation

When a user asks about a company (e.g., "Tell me about Apple"), clarify what they want:
- Company overview
- Latest news
- Earnings analysis
- Valuation metrics
- Investment analysis
- Stock performance"""
        
        if user_context:
            context_additions = []
            
            if user_context.get("name"):
                context_additions.append(f"User's name: {user_context['name']}")
            
            if user_context.get("role"):
                context_additions.append(f"User's role: {user_context['role']}")
            
            if user_context.get("investment_interests"):
                context_additions.append(f"Investment interests: {user_context['investment_interests']}")
            
            if user_context.get("preferred_sectors"):
                context_additions.append(f"Preferred sectors: {user_context['preferred_sectors']}")
            
            if context_additions:
                base_prompt += "\n\nUser Context:\n" + "\n".join(context_additions)
        
        return base_prompt
    
    async def detect_intent(self, user_message: str) -> str:
        """Detect the intent of the user's message."""
        intent_prompt = f"""Classify the user's intent into one of these categories:
- stock_analysis: Request for stock analysis or information
- market_overview: Request for market overview or trends
- company_info: Request for company information
- portfolio: Request about portfolio management
- general: General financial question
- greeting: Greeting or casual conversation
- document_analysis: Request to analyze a document

User message: {user_message}

Return only the category name."""
        
        response = await self.ai_provider.generate_response(
            prompt=intent_prompt,
            temperature=0.1
        )
        
        return response.strip().lower()
    
    def add_to_conversation_history(
        self,
        user_id: int,
        role: str,
        content: str
    ):
        """Add message to conversation history."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "role": role,
            "content": content
        })
        
        # Keep only last 20 messages
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
    
    def get_conversation_history(self, user_id: int) -> List[Dict[str, str]]:
        """Get conversation history for a user."""
        return self.conversation_history.get(user_id, [])
    
    async def handle_follow_up(
        self,
        user_message: str,
        user_id: int,
        conversation_context: Dict[str, Any]
    ) -> Optional[str]:
        """Handle follow-up questions with context awareness."""
        # Check if this is a follow-up question
        follow_up_indicators = [
            "what about", "tell me more", "elaborate", "explain further",
            "and", "also", "what else", "how about", "compared to"
        ]
        
        is_follow_up = any(
            indicator in user_message.lower() 
            for indicator in follow_up_indicators
        )
        
        if not is_follow_up:
            return None
        
        # Get context from previous conversation
        last_symbol = conversation_context.get("last_symbol")
        last_intent = conversation_context.get("last_intent")
        
        if not last_symbol and not last_intent:
            return None
        
        # Build context-aware response
        context_prompt = f"""The user is asking a follow-up question.

Previous context:
- Last discussed symbol: {last_symbol or 'None'}
- Last intent: {last_intent or 'None'}
- User's question: {user_message}

Provide a response that naturally continues the conversation. Reference the previous context when relevant."""
        
        response = await self.ai_provider.generate_response(
            prompt=context_prompt,
            context="You are a conversational AI assistant. Handle follow-up questions naturally by maintaining context from previous messages.",
            temperature=0.7
        )
        
        return response
    
    async def detect_implicit_context(
        self,
        user_message: str,
        conversation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect implicit context in user's message."""
        detected_context = {}
        
        # Check if user is referring to previous symbol without naming it
        last_symbol = conversation_context.get("last_symbol")
        
        if last_symbol and last_symbol not in user_message.upper():
            # Check for pronouns or implicit references
            implicit_refs = ["it", "the stock", "the company", "they", "their"]
            if any(ref in user_message.lower() for ref in implicit_refs):
                detected_context["implicit_symbol"] = last_symbol
        
        # Check for "valuation" or "metrics" references
        if "valuation" in user_message.lower() or "metrics" in user_message.lower():
            detected_context["focus"] = "financial_metrics"
        
        return detected_context
