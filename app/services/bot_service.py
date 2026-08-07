from typing import Optional
from sqlalchemy.orm import Session
from app.models import get_db
from app.repositories import (
    UserRepository,
    ConversationRepository,
    MessageRepository,
    WatchlistRepository,
    ResearchRepository,
    DocumentRepository,
    PreferenceRepository
)
from app.ai.agents import (
    ConversationAgent,
    FinanceAgent,
    DocumentAgent,
    MemoryAgent
)
from app.ai.providers import OpenAIProvider, AnthropicProvider, GoogleProvider
from app.config.settings import get_settings


class BotService:
    """Service layer for bot operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.ai_provider = self._get_ai_provider()
        self.conversation_agent = ConversationAgent(self.ai_provider)
        self.finance_agent = FinanceAgent(self.ai_provider)
        self.document_agent = DocumentAgent(self.ai_provider)
        self.memory_agent = MemoryAgent(self.ai_provider)
    
    def _get_ai_provider(self):
        """Get the configured AI provider."""
        provider_name = self.settings.ai_provider.lower()
        
        if provider_name == "openai":
            return OpenAIProvider(api_key=self.settings.openai_api_key)
        elif provider_name == "anthropic":
            return AnthropicProvider(api_key=self.settings.anthropic_api_key)
        elif provider_name == "google":
            return GoogleProvider(api_key=self.settings.google_api_key)
        else:
            raise ValueError(f"Unknown AI provider: {provider_name}")
    
    def _get_db_session(self):
        """Get a database session."""
        return next(get_db())
    
    async def initialize_user(
        self,
        telegram_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str]
    ) -> None:
        """Initialize a user in the database."""
        db = self._get_db_session()
        try:
            user_repo = UserRepository(db)
            user_repo.get_or_create_by_telegram_id(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            user_repo.update_last_interaction(
                user_repo.get_by_telegram_id(telegram_id)
            )
        finally:
            db.close()
    
    async def process_text_message(
        self,
        user_id: int,
        message_text: str
    ) -> str:
        """Process a text message from the user."""
        db = self._get_db_session()
        try:
            user_repo = UserRepository(db)
            conversation_repo = ConversationRepository(db)
            message_repo = MessageRepository(db)
            preference_repo = PreferenceRepository(db)
            
            # Get or create user
            user = user_repo.get_or_create_by_telegram_id(user_id)
            user_repo.update_last_interaction(user)
            
            # Get or create conversation
            conversation = conversation_repo.get_active_conversation(user.id)
            if not conversation:
                conversation = conversation_repo.create(user_id=user.id)
            
            # Save user message
            message_repo.create_user_message(
                conversation_id=conversation.id,
                content=message_text,
                message_type="text"
            )
            
            # Get conversation history
            history = message_repo.get_conversation_history(
                conversation.id,
                limit=self.settings.max_conversation_history
            )
            
            # Get user preferences for context
            preferences = preference_repo.get_or_create_preferences(user.id)
            user_context = {
                "name": user.name,
                "role": user.role,
                "investment_interests": user.investment_interests,
                "preferred_sectors": user.preferred_sectors,
                "response_style": preferences.response_style
            }
            
            # Detect intent
            intent = await self.conversation_agent.detect_intent(message_text)
            
            # Route to appropriate agent
            if intent == "stock_analysis":
                # Extract symbol from message
                import re
                symbols = re.findall(r'\b[A-Z]{2,5}\b', message_text.upper())
                if symbols:
                    response = await self.finance_agent.analyze_stock(symbols[0])
                else:
                    response = await self.conversation_agent.process_message(
                        message_text, history, user_context
                    )
            elif intent == "market_overview":
                response = await self.finance_agent.get_market_overview()
            else:
                response = await self.conversation_agent.process_message(
                    message_text, history, user_context
                )
            
            # Save assistant response
            message_repo.create_assistant_message(
                conversation_id=conversation.id,
                content=response
            )
            
            return response
            
        finally:
            db.close()
    
    async def analyze_stock(self, user_id: int, symbol: str) -> str:
        """Analyze a stock for the user."""
        db = self._get_db_session()
        try:
            user_repo = UserRepository(db)
            research_repo = ResearchRepository(db)
            
            user = user_repo.get_by_telegram_id(user_id)
            
            # Perform analysis
            analysis = await self.finance_agent.analyze_stock(symbol)
            
            # Save to research history
            research_repo.create_research(
                user_id=user.id,
                query=f"Analyze {symbol}",
                query_type="stock_analysis",
                summary=analysis.get("analysis"),
                confidence_score=int(analysis.get("confidence", 0) * 100)
            )
            
            return analysis.get("analysis", "Analysis failed. Please try again.")
            
        finally:
            db.close()
    
    async def get_market_overview(self, user_id: int) -> str:
        """Get market overview for the user."""
        return await self.finance_agent.get_market_overview()
    
    async def get_watchlist(self, user_id: int) -> str:
        """Get user's watchlist."""
        db = self._get_db_session()
        try:
            user_repo = UserRepository(db)
            watchlist_repo = WatchlistRepository(db)
            
            user = user_repo.get_by_telegram_id(user_id)
            watchlist = watchlist_repo.get_user_watchlist(user.id)
            
            if not watchlist:
                return "Your watchlist is empty. Add stocks with /watchlist add <symbol>"
            
            response = "📋 Your Watchlist:\n\n"
            for item in watchlist:
                response += f"• {item.symbol} - {item.company_name or 'N/A'}\n"
                if item.notes:
                    response += f"  Note: {item.notes}\n"
            
            return response
            
        finally:
            db.close()
    
    async def process_document(self, user_id: int, document) -> str:
        """Process a document upload."""
        db = self._get_db_session()
        try:
            user_repo = UserRepository(db)
            document_repo = DocumentRepository(db)
            
            user = user_repo.get_by_telegram_id(user_id)
            
            # Create document record
            doc = document_repo.create_document(
                user_id=user.id,
                file_type="pdf",
                file_id=document.file_id,
                file_name=document.file_name,
                file_size=document.file_size
            )
            
            # Download and process document (placeholder)
            # In production, you would download the file and extract text
            
            return f"📄 Document received: {document.file_name}\n\nProcessing... This feature requires document download implementation. The document has been saved to your history."
            
        finally:
            db.close()
    
    async def process_image(self, user_id: int, photo) -> str:
        """Process an image upload."""
        db = self._get_db_session()
        try:
            user_repo = UserRepository(db)
            document_repo = DocumentRepository(db)
            
            user = user_repo.get_by_telegram_id(user_id)
            
            # Create document record
            doc = document_repo.create_document(
                user_id=user.id,
                file_type="image",
                file_id=photo.file_id,
                file_size=photo.file_size
            )
            
            return "🖼️ Image received. Chart analysis requires image processing implementation. The image has been saved to your history."
            
        finally:
            db.close()
    
    async def process_voice(self, user_id: int, voice) -> str:
        """Process a voice message."""
        db = self._get_db_session()
        try:
            user_repo = UserRepository(db)
            
            user = user_repo.get_by_telegram_id(user_id)
            
            return "🎤 Voice message received. Voice-to-text processing requires additional implementation. Please use text messages for now."
            
        finally:
            db.close()
