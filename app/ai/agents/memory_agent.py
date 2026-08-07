from typing import Optional, Dict, Any
from app.ai.providers import BaseAIProvider


class MemoryAgent:
    """Agent for managing user memory and personalization."""
    
    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider
    
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
