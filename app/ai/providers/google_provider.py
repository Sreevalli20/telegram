from typing import Optional, Dict, Any
import google.generativeai as genai
from app.ai.providers.base_provider import BaseAIProvider


class GoogleProvider(BaseAIProvider):
    """Google (Gemini) provider implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        super().__init__(api_key)
        self.model_name = model
        self._model = None
    
    def _ensure_model(self):
        """Lazy initialization of Google model."""
        if self._model is None:
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY is not configured. Please set the GOOGLE_API_KEY environment variable to use Google features.")
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)
        return self._model
    
    @property
    def model(self):
        """Get the Google model (lazy initialization)."""
        return self._ensure_model()
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from Google Gemini."""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        response = await self.model.generate_content_async(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        
        return response.text
    
    async def summarize(
        self,
        text: str,
        max_length: int = 200
    ) -> str:
        """Summarize text using Google Gemini."""
        prompt = f"Summarize the following text in {max_length} words or less:\n\n{text}"
        
        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.3)
        )
        
        return response.text
    
    async def analyze_document(
        self,
        document_text: str,
        analysis_type: str = "financial"
    ) -> Dict[str, Any]:
        """Analyze a document using Google Gemini."""
        prompt = f"You are a financial analyst. Analyze the following {analysis_type} document:\n\n{document_text}"
        
        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.3)
        )
        
        return {
            "analysis": response.text,
            "provider": "google",
            "model": self.model_name
        }
    
    async def extract_information(
        self,
        text: str,
        information_type: str
    ) -> Dict[str, Any]:
        """Extract specific information from text."""
        prompt = f"Extract {information_type} from the following text. Return as structured JSON:\n\n{text}"
        
        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.1)
        )
        
        import json
        return json.loads(response.text)
    
    async def chat_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a chat completion with message history."""
        # Convert messages to Gemini format
        chat_history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})
        
        chat = self.model.start_chat(history=chat_history)
        response = await chat.send_message_async(
            messages[-1]["content"],
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        
        return response.text
