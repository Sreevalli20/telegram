from typing import Optional, Dict, Any
from anthropic import AsyncAnthropic
from app.ai.providers.base_provider import BaseAIProvider


class AnthropicProvider(BaseAIProvider):
    """Anthropic (Claude) provider implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key)
        self.model = model
        self._client = None
    
    def _ensure_client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY is not configured. Please set the ANTHROPIC_API_KEY environment variable to use Anthropic features.")
            self._client = AsyncAnthropic(api_key=self.api_key)
        return self._client
    
    @property
    def client(self):
        """Get the Anthropic client (lazy initialization)."""
        return self._ensure_client()
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from Anthropic."""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens or 1024,
            temperature=temperature,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        return response.content[0].text
    
    async def summarize(
        self,
        text: str,
        max_length: int = 200
    ) -> str:
        """Summarize text using Anthropic."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize the following text in {max_length} words or less:\n\n{text}"
                }
            ]
        )
        
        return response.content[0].text
    
    async def analyze_document(
        self,
        document_text: str,
        analysis_type: str = "financial"
    ) -> Dict[str, Any]:
        """Analyze a document using Anthropic."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": f"You are a financial analyst. Analyze the following {analysis_type} document:\n\n{document_text}"
                }
            ]
        )
        
        return {
            "analysis": response.content[0].text,
            "provider": "anthropic",
            "model": self.model
        }
    
    async def extract_information(
        self,
        text: str,
        information_type: str
    ) -> Dict[str, Any]:
        """Extract specific information from text."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": f"Extract {information_type} from the following text. Return as structured JSON:\n\n{text}"
                }
            ]
        )
        
        import json
        return json.loads(response.content[0].text)
    
    async def chat_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a chat completion with message history."""
        # Convert OpenAI-style messages to Anthropic format
        anthropic_messages = []
        for msg in messages:
            role = msg["role"]
            if role == "assistant":
                role = "assistant"
            else:
                role = "user"
            anthropic_messages.append({"role": role, "content": msg["content"]})
        
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens or 1024,
            temperature=temperature,
            messages=anthropic_messages
        )
        
        return response.content[0].text
