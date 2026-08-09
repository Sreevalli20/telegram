from typing import Dict, Any, Optional
from app.ai.providers import BaseAIProvider
import pypdf
from io import BytesIO


class DocumentAgent:
    """Agent for document analysis and processing with PDF support."""
    
    def __init__(self, ai_provider: BaseAIProvider):
        self.ai_provider = ai_provider
        self.document_context = {}  # Store document context for chat
    
    def extract_text_from_pdf(self, pdf_file: BytesIO) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = pypdf.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"
    
    async def analyze_financial_document(
        self,
        document_text: str,
        document_type: str = "general",
        document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze a financial document (PDF, report, etc.)."""
        system_prompt = f"""You are a professional financial document analyst. Analyze this {document_type} document.

Extract and provide a structured analysis with:
1. **Executive Summary**: Brief overview of the document's key points
2. **Financial Highlights**: Revenue, Profit, EBITDA, Cash Flow if available
3. **Key Metrics**: Important financial ratios and metrics
4. **Growth Analysis**: Revenue growth, profit growth trends
5. **Risks**: Major risk factors mentioned
6. **Management Commentary**: Key points from management discussion
7. **Important Changes**: Significant changes from previous periods
8. **Investor Questions**: Important questions investors should ask

Be specific and data-driven. If information is not available in the document, clearly state that limitation."""
        
        analysis = await self.ai_provider.generate_response(
            prompt=f"Analyze this financial document:\n\n{document_text[:15000]}",  # Limit to avoid token limits
            context=system_prompt,
            temperature=0.5
        )
        
        # Store document context if document_id provided
        if document_id:
            self.document_context[document_id] = {
                "text": document_text,
                "type": document_type,
                "analysis": analysis
            }
        
        return {
            "document_type": document_type,
            "analysis": analysis,
            "document_id": document_id,
            "available": True
        }
    
    async def extract_financial_data(
        self,
        document_text: str
    ) -> Dict[str, Any]:
        """Extract structured financial data from document."""
        extraction_prompt = """Extract the following financial data from the document if available. Return as JSON format:

{
  "revenue": "value or null",
  "net_income": "value or null", 
  "ebitda": "value or null",
  "eps": "value or null",
  "profit_margin": "value or null",
  "revenue_growth": "value or null",
  "cash_flow": "value or null",
  "debt": "value or null",
  "assets": "value or null",
  "liabilities": "value or null",
  "equity": "value or null"
}

If data is not available in the document, use null. Be precise with the values."""
        
        extracted_data = await self.ai_provider.generate_response(
            prompt=f"Extract financial data from this document:\n\n{document_text[:10000]}",
            context=extraction_prompt,
            temperature=0.1
        )
        
        return {
            "extracted_data": extracted_data,
            "available": True
        }
    
    async def summarize_document(
        self,
        document_text: str,
        max_length: int = 300
    ) -> str:
        """Summarize a document concisely."""
        summary_prompt = f"""Summarize this financial document in under {max_length} words.

Focus on:
- Key financial results
- Major announcements
- Important changes
- Overall performance

Be concise and specific."""
        
        summary = await self.ai_provider.generate_response(
            prompt=f"Summarize this document:\n\n{document_text[:10000]}",
            context=summary_prompt,
            temperature=0.5
        )
        
        return summary
    
    async def chat_about_document(
        self,
        question: str,
        document_id: str,
        conversation_history: Optional[list] = None
    ) -> str:
        """Chat about a previously uploaded document."""
        if document_id not in self.document_context:
            return "Document not found. Please upload the document again."
        
        document_data = self.document_context[document_id]
        document_text = document_data["text"]
        document_type = document_data["type"]
        
        # Build context with conversation history
        context_parts = [f"Document Type: {document_type}"]
        
        if conversation_history:
            context_parts.append("Previous conversation:")
            for msg in conversation_history[-5]:  # Last 5 messages
                context_parts.append(f"{msg['role']}: {msg['content']}")
        
        context_parts.append(f"\nDocument content:\n{document_text[:15000]}")
        
        system_prompt = """You are a financial document analyst answering questions about a specific document.

Use the provided document content to answer the user's question accurately. If the information is not in the document, clearly state that.

Be specific and reference the document when possible. Avoid making up information not present in the document."""
        
        response = await self.ai_provider.generate_response(
            prompt=f"Question: {question}\n\nContext:\n{chr(10).join(context_parts)}",
            context=system_prompt,
            temperature=0.5
        )
        
        return response
    
    async def compare_documents(
        self,
        document1_text: str,
        document2_text: str,
        document1_type: str = "Document 1",
        document2_type: str = "Document 2"
    ) -> str:
        """Compare two financial documents."""
        comparison_prompt = f"""Compare these two financial documents:

{document1_type}:
{document1_text[:10000]}

{document2_type}:
{document2_text[:10000]}

Provide a structured comparison highlighting:
- Revenue changes
- Profit changes
- Key metric differences
- Risk factor changes
- Overall performance comparison
- Important trends or reversals"""

        comparison = await self.ai_provider.generate_response(
            prompt=comparison_prompt,
            context="You are a financial analyst comparing two documents. Be specific and data-driven.",
            temperature=0.5
        )
        
        return comparison
    
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
- Overall sentiment
- Actionable insights"""

        response = await self.ai_provider.generate_response(
            prompt=f"Analyze this chart: {image_description}",
            context=system_prompt,
            temperature=0.5
        )
        
        return response
    
    def clear_document_context(self, document_id: str):
        """Clear document context for a specific document."""
        if document_id in self.document_context:
            del self.document_context[document_id]
    
    def get_document_context(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get stored document context."""
        return self.document_context.get(document_id)
