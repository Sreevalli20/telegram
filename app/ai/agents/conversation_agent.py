from typing import Optional, List
from app.ai.providers import BaseAIProvider


class ConversationAgent:
    """Agent for handling conversational interactions with context awareness."""
    
    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider
    
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
