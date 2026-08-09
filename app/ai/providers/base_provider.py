from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from the AI model."""
        pass
    
    @abstractmethod
    async def summarize(
        self,
        text: str,
        max_length: int = 200
    ) -> str:
        """Summarize the given text."""
        pass
    
    @abstractmethod
    async def analyze_document(
        self,
        document_text: str,
        analysis_type: str = "financial"
    ) -> Dict[str, Any]:
        """Analyze a document and extract insights."""
        pass
    
    @abstractmethod
    async def extract_information(
        self,
        text: str,
        information_type: str
    ) -> Dict[str, Any]:
        """Extract specific information from text."""
        pass
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a chat completion with message history."""
        pass
