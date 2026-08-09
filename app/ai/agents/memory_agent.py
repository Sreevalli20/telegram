from typing import Optional, Dict, Any, List
from app.ai.providers import BaseAIProvider
from datetime import datetime
import json


class MemoryAgent:
    """Agent for managing user memory and personalization with enhanced intelligence."""
    
    def __init__(self, ai_provider: Optional[BaseAIProvider] = None):
        self.ai_provider = ai_provider
        self.user_memories = {}  # In-memory cache (in production, use database)
        self.conversation_contexts = {}  # Track conversation contexts per user
    
    async def extract_user_profile(
        self,
        conversation_history: list
    ) -> Dict[str, Any]:
        """Extract user profile information from conversation history."""
        system_prompt = """Analyze the conversation history and extract user profile information including:
- Investment experience level
- Risk tolerance
- Investment goals
- Preferred sectors/companies
- Communication style preferences

Return as structured JSON. If information is not available, use null."""
        
        # Convert conversation history to text
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation_history
        ])
        
        profile = await self.ai_provider.extract_information(
            text=conversation_text,
            information_type="user profile"
        )
        
        return profile
    
    async def summarize_conversation(
        self,
        conversation_history: list
    ) -> str:
        """Summarize a conversation for memory storage."""
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation_history
        ])
        
        summary = await self.ai_provider.summarize(
            text=conversation_text,
            max_length=200
        )
        
        return summary
    
    async def identify_interests(
        self,
        conversation_history: list
    ) -> list:
        """Identify user's investment interests from conversations."""
        system_prompt = """Analyze the conversation and identify the user's investment interests.

Extract:
- Specific companies mentioned
- Sectors of interest
- Investment themes
- Asset classes mentioned

Return as a structured list."""
        
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation_history
        ])
        
        response = await self.ai_provider.generate_response(
            prompt="Extract investment interests",
            context=system_prompt + "\n\n" + conversation_text,
            temperature=0.3
        )
        
        # Parse response into list (simplified)
        return [line.strip() for line in response.split("\n") if line.strip()]
    
    async def generate_personalized_insight(
        self,
        user_profile: Dict[str, Any],
        market_context: str
    ) -> str:
        """Generate personalized insight based on user profile."""
        system_prompt = f"""You are a personalized financial advisor. Generate insights based on the user's profile.

User Profile:
{user_profile}

Market Context:
{market_context}

Provide personalized insights that consider:
- User's experience level
- Risk tolerance
- Investment goals
- Past interests

Be specific and actionable."""
        
        response = await self.ai_provider.generate_response(
            prompt="Generate personalized investment insight",
            context=system_prompt,
            temperature=0.7
        )
        
        return response
    
    def update_user_memory(self, user_id: int, key: str, value: Any):
        """Update user memory with a key-value pair."""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = {}
        
        self.user_memories[user_id][key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
    
    def get_user_memory(self, user_id: int, key: Optional[str] = None) -> Any:
        """Get user memory value(s)."""
        if user_id not in self.user_memories:
            return None
        
        if key:
            return self.user_memories[user_id].get(key, {}).get("value")
        return self.user_memories[user_id]
    
    def track_conversation_context(
        self,
        user_id: int,
        last_intent: str,
        last_symbol: Optional[str] = None,
        last_topic: Optional[str] = None
    ):
        """Track conversation context for follow-up intelligence."""
        self.conversation_contexts[user_id] = {
            "last_intent": last_intent,
            "last_symbol": last_symbol,
            "last_topic": last_topic,
            "updated_at": datetime.now().isoformat()
        }
    
    def get_conversation_context(self, user_id: int) -> Dict[str, Any]:
        """Get conversation context for a user."""
        return self.conversation_contexts.get(user_id, {})
    
    async def learn_from_interaction(
        self,
        user_id: int,
        user_message: str,
        intent: str,
        entities: Dict[str, Any]
    ):
        """Learn from user interaction to improve future responses."""
        # Extract companies mentioned
        if entities.get("symbols"):
            existing_symbols = self.get_user_memory(user_id, "mentioned_symbols") or []
            new_symbols = list(set(entities["symbols"]) - set(existing_symbols))
            if new_symbols:
                all_symbols = existing_symbols + new_symbols
                self.update_user_memory(user_id, "mentioned_symbols", all_symbols)
        
        # Track intent patterns
        intent_counts = self.get_user_memory(user_id, "intent_counts") or {}
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
        self.update_user_memory(user_id, "intent_counts", intent_counts)
        
        # Extract preferences from message
        if "interested in" in user_message.lower() or "i like" in user_message.lower():
            await self._extract_preferences(user_id, user_message)
    
    async def _extract_preferences(self, user_id: int, message: str):
        """Extract user preferences from message."""
        preference_prompt = f"""Extract investment preferences from this message: "{message}"

Look for:
- Preferred sectors (e.g., technology, healthcare)
- Investment styles (e.g., growth, value, dividend)
- Risk preferences
- Time horizons

Return as JSON with keys: sectors, style, risk, horizon"""
        
        try:
            preferences = await self.ai_provider.generate_response(
                prompt=preference_prompt,
                temperature=0.3
            )
            self.update_user_memory(user_id, "preferences", preferences)
        except Exception:
            pass
    
    async def get_personalized_context(self, user_id: int) -> Dict[str, Any]:
        """Get personalized context for AI responses."""
        context = {
            "user_id": user_id,
            "conversation_context": self.get_conversation_context(user_id),
            "memory": self.get_user_memory(user_id)
        }
        
        # Build human-readable context
        readable_context = []
        
        if context["memory"]:
            if context["memory"].get("mentioned_symbols"):
                readable_context.append(f"User has shown interest in: {', '.join(context['memory']['mentioned_symbols'])}")
            
            if context["memory"].get("preferences"):
                readable_context.append(f"User preferences: {context['memory']['preferences']}")
        
        if context["conversation_context"]:
            if context["conversation_context"].get("last_symbol"):
                readable_context.append(f"Last discussed: {context['conversation_context']['last_symbol']}")
        
        context["readable_context"] = readable_context
        return context
    
    async def suggest_follow_up_questions(
        self,
        user_id: int,
        current_intent: str,
        current_symbol: Optional[str] = None
    ) -> List[str]:
        """Suggest relevant follow-up questions based on context."""
        conversation_context = self.get_conversation_context(user_id)
        user_memory = self.get_user_memory(user_id)
        
        suggestions = []
        
        # Context-aware suggestions
        if current_intent == "company_research" and current_symbol:
            suggestions = [
                f"How does {current_symbol} compare to its competitors?",
                f"What are the main risks for {current_symbol}?",
                f"Is {current_symbol} currently overvalued or undervalued?"
            ]
        elif current_intent == "market_analysis":
            suggestions = [
                "Which sectors are performing best today?",
                "What are the biggest market movers?",
                "How is the market sentiment overall?"
            ]
        elif current_intent == "stock_lookup":
            suggestions = [
                "Show me the company overview",
                "What are the key financial metrics?",
                "Add this to my watchlist"
            ]
        
        # Personalized suggestions based on memory
        if user_memory and user_memory.get("mentioned_symbols"):
            other_symbols = [s for s in user_memory["mentioned_symbols"] if s != current_symbol]
            if other_symbols:
                suggestions.append(f"Compare with {other_symbols[0]}")
        
        return suggestions[:3]  # Return top 3 suggestions
