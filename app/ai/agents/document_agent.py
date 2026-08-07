from typing import Dict, Any, Optional
from app.ai.providers import BaseAIProvider


class DocumentAgent:
    """Agent for document analysis and processing."""
    
    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider
    
    async def analyze_financial_document(
        self,
        document_text: str,
        document_type: str = "general"
    ) -> Dict[str, Any]:
        """Analyze a financial document (PDF, report, etc.)."""
        system_prompt = f"""You are a financial document analyst. Analyze this {document_type} document.

Extract and provide:
1. Executive summary
2. Key financial metrics
3. Important insights
4. Risk factors
5. Recommendations or conclusions

Be thorough and specific. If the document is unclear or incomplete, note that in your analysis."""
        
        analysis = await self.ai_provider.analyze_document(
            document_text=document_text,
            analysis_type=document_type
        )
        
        return analysis
    
    async def extract_financial_data(
        self,
        document_text: str
    ) -> Dict[str, Any]:
        """Extract structured financial data from document."""
        extraction_prompt = """Extract the following financial data from the document if available:
- Revenue
- Net Income
- EPS
- P/E Ratio
- Market Cap
- Debt/Equity Ratio
- ROE
- Profit Margins

Return as structured JSON. If data is not available, use null."""
        
        extracted_data = await self.ai_provider.extract_information(
            text=document_text,
            information_type="financial metrics"
        )
        
        return extracted_data
    
    async def summarize_document(
        self,
        document_text: str,
        max_length: int = 300
    ) -> str:
        """Summarize a document."""
        summary = await self.ai_provider.summarize(
            text=document_text,
            max_length=max_length
        )
        
        return summary
    
    async def analyze_chart_image(
        self,
        image_description: str
    ) -> str:
        """Analyze a chart or graph image (via description)."""
        system_prompt = """You are a technical analyst. Analyze this chart/image description.

Provide:
- Chart type identification
- Key trends and patterns
- Support/resistance levels (if applicable)
- Technical indicators interpretation
- Overall sentiment"""

        response = await self.ai_provider.generate_response(
            prompt=f"Analyze this chart: {image_description}",
            context=system_prompt,
            temperature=0.5
        )
        
        return response
