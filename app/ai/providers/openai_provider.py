from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from app.ai.providers.base_provider import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        super().__init__(api_key)
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from OpenAI."""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    async def summarize(
        self,
        text: str,
        max_length: int = 200
    ) -> str:
        """Summarize text using OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": f"Summarize the following text in {max_length} words or less."
                },
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    async def analyze_document(
        self,
        document_text: str,
        analysis_type: str = "financial"
    ) -> Dict[str, Any]:
        """Analyze a document using OpenAI."""
        system_prompt = f"You are a financial analyst. Analyze the following {analysis_type} document."
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": document_text}
            ],
            temperature=0.3
        )
        
        return {
            "analysis": response.choices[0].message.content,
            "provider": "openai",
            "model": self.model
        }
    
    async def extract_information(
        self,
        text: str,
        information_type: str
    ) -> Dict[str, Any]:
        """Extract specific information from text."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": f"Extract {information_type} from the following text. Return as structured JSON."
                },
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    async def chat_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a chat completion with message history."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
