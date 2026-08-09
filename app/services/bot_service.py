from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import get_db
from app.repositories import (
    UserRepository,
    ConversationRepository,
    MessageRepository,
    WatchlistRepository,
    ResearchRepository,
    DocumentRepository,
    PreferenceRepository,
    NotificationRepository
)
from app.ai.agents import (
    ConversationAgent,
    FinanceAgent,
    DocumentAgent,
    MemoryAgent
)
from app.ai.intent_detector import IntentDetector
from app.ai.providers import OpenAIProvider, AnthropicProvider, GoogleProvider
from app.config.settings import get_settings
from app.services import (
    WatchlistService,
    AlertService,
    DailyIntelligenceService,
    VoiceService,
    ImageService,
    ExplanationService,
    ResponseFormatter
)
from app.workers.background_worker import BackgroundWorker


class BotService:
    """Service layer for bot operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.ai_provider = self._get_ai_provider()
        self.conversation_agent = ConversationAgent(self.ai_provider)
        self.finance_agent = FinanceAgent(self.ai_provider)
        self.document_agent = DocumentAgent(self.ai_provider)
        self.memory_agent = MemoryAgent(self.ai_provider)
        self.intent_detector = IntentDetector()
        self.response_formatter = ResponseFormatter()
        self.background_worker = BackgroundWorker()
        
        # Initialize services (will be created with DB session when needed)
        self.watchlist_service = None
        self.alert_service = None
        self.daily_intelligence_service = None
        self.voice_service = VoiceService()
        self.image_service = ImageService()
        self.explanation_service = ExplanationService(self.ai_provider)
    
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
    
    def _initialize_services(self, db: Session):
        """Initialize services that require DB session."""
        if not self.watchlist_service:
            self.watchlist_service = WatchlistService(db)
        if not self.alert_service:
            self.alert_service = AlertService(db)
        if not self.daily_intelligence_service:
            self.daily_intelligence_service = DailyIntelligenceService(db, self.ai_provider)
    
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
        """Process a text message from the user with enhanced routing."""
        db = self._get_db_session()
        try:
            self._initialize_services(db)
            
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
            
            # Detect intent with enhanced detector
            intent_result = self.intent_detector.detect_intent(message_text)
            intent = intent_result["intent"]
            entities = intent_result["entities"]
            
            # Track conversation context
            self.memory_agent.track_conversation_context(
                user_id=user.id,
                last_intent=intent,
                last_symbol=entities.get("symbols", [None])[0] if entities.get("symbols") else None,
                last_topic=entities.get("topic")
            )
            
            # Learn from interaction
            await self.memory_agent.learn_from_interaction(
                user_id=user.id,
                user_message=message_text,
                intent=intent,
                entities=entities
            )
            
            # Route to appropriate handler
            response = await self._route_intent(
                intent=intent,
                entities=entities,
                message_text=message_text,
                user_id=user.id,
                db_user=user,
                history=history,
                user_context=user_context
            )
            
            # Format response
            suggestions = self.response_formatter.generate_suggestions(
                intent=intent,
                symbol=entities.get("symbols", [None])[0] if entities.get("symbols") else None
            )
            formatted_response = self.response_formatter.format_response(
                content=response,
                intent=intent,
                include_emoji=True,
                include_suggestions=True,
                suggestions=suggestions
            )
            
            # Truncate if too long
            formatted_response = self.response_formatter.truncate_response(formatted_response)
            
            # Save assistant response
            message_repo.create_assistant_message(
                conversation_id=conversation.id,
                content=formatted_response
            )
            
            # Add to conversation history
            self.conversation_agent.add_to_conversation_history(user.id, "user", message_text)
            self.conversation_agent.add_to_conversation_history(user.id, "assistant", formatted_response)
            
            return formatted_response
            
        finally:
            db.close()
    
    async def _route_intent(
        self,
        intent: str,
        entities: Dict[str, Any],
        message_text: str,
        user_id: int,
        db_user,
        history: list,
        user_context: Dict[str, Any]
    ) -> str:
        """Route intent to appropriate handler."""
        symbols = entities.get("symbols", [])
        
        if intent == "stock_lookup" and symbols:
            return await self._handle_stock_lookup(symbols[0])
        elif intent == "company_research" and symbols:
            return await self._handle_company_research(symbols[0])
        elif intent == "market_analysis":
            return await self._handle_market_analysis()
        elif intent == "comparison" and len(symbols) >= 2:
            return await self._handle_comparison(symbols[:2])
        elif intent == "news_request":
            return await self._handle_news_request(symbols[0] if symbols else None)
        elif intent == "watchlist":
            return await self._handle_watchlist(entities, user_id)
        elif intent == "alert":
            return await self._handle_alert(entities, user_id)
        elif intent == "explanation":
            concept = entities.get("concept")
            if concept:
                return await self._handle_explanation(concept)
        elif intent == "document_chat":
            return await self._handle_document_chat(message_text, user_id)
        elif intent == "daily_briefing":
            return await self._handle_daily_briefing(user_id)
        
        # Default to conversation agent
        return await self.conversation_agent.process_message(
            message_text, history, user_context
        )
    
    async def _handle_stock_lookup(self, symbol: str) -> str:
        """Handle stock lookup intent."""
        result = await self.finance_agent.get_stock_price(symbol)
        if result.get("available"):
            analysis = await self.finance_agent.analyze_stock(symbol)
            return self.response_formatter.format_stock_response(
                symbol=symbol,
                price_data=result,
                analysis=analysis.get("analysis", "Analysis unavailable")
            )
        return f"Unable to fetch data for {symbol}. Please check the symbol and try again."
    
    async def _handle_company_research(self, symbol: str) -> str:
        """Handle company research intent."""
        result = await self.finance_agent.get_company_research(symbol)
        return result.get("analysis", "Research unavailable")
    
    async def _handle_market_analysis(self) -> str:
        """Handle market analysis intent."""
        result = await self.finance_agent.get_market_overview()
        return result.get("analysis", "Market overview unavailable")
    
    async def _handle_comparison(self, symbols: list) -> str:
        """Handle comparison intent."""
        result = await self.finance_agent.compare_companies(symbols[0], symbols[1])
        return result.get("comparison_analysis", "Comparison unavailable")
    
    async def _handle_news_request(self, symbol: Optional[str]) -> str:
        """Handle news request intent."""
        if symbol:
            result = await self.finance_agent.get_financial_news(symbol)
        else:
            result = await self.finance_agent.get_financial_news()
        return result.get("analysis", "News unavailable")
    
    async def _handle_watchlist(self, entities: Dict[str, Any], user_id: int) -> str:
        """Handle watchlist intent."""
        action = entities.get("action", "view")
        symbols = entities.get("symbols", [])
        
        if action == "add" and symbols:
            result = await self.watchlist_service.add_to_watchlist(user_id, symbols[0])
            return result.get("message", "Watchlist operation completed")
        elif action == "remove" and symbols:
            result = self.watchlist_service.remove_from_watchlist(user_id, symbols[0])
            return result.get("message", "Watchlist operation completed")
        elif action == "alert" and symbols:
            alert_above = entities.get("alert_above")
            alert_below = entities.get("alert_below")
            result = self.watchlist_service.set_price_alert(user_id, symbols[0], alert_above, alert_below)
            return result.get("message", "Alert set")
        else:
            watchlist_data = self.watchlist_service.get_watchlist(user_id)
            return self.response_formatter.format_watchlist_response(watchlist_data)
    
    async def _handle_alert(self, entities: Dict[str, Any], user_id: int) -> str:
        """Handle alert intent."""
        symbols = entities.get("symbols", [])
        if symbols:
            alert_above = entities.get("alert_above")
            alert_below = entities.get("alert_below")
            result = self.watchlist_service.set_price_alert(user_id, symbols[0], alert_above, alert_below)
            return result.get("message", "Alert operation completed")
        return "Please specify a symbol and alert threshold."
    
    async def _handle_explanation(self, concept: str) -> str:
        """Handle explanation intent."""
        result = await self.explanation_service.explain_concept(concept)
        return result.get("explanation", "Explanation unavailable")
    
    async def _handle_document_chat(self, message_text: str, user_id: int) -> str:
        """Handle document chat intent."""
        # Check if there's an active document context
        document_context = self.document_agent.get_document_context(f"{user_id}_active")
        if document_context:
            response = await self.document_agent.chat_about_document(
                question=message_text,
                document_id=f"{user_id}_active"
            )
            return response
        return "No document context found. Please upload a document first."
    
    async def _handle_daily_briefing(self, user_id: int) -> str:
        """Handle daily briefing intent."""
        result = await self.daily_intelligence_service.generate_morning_brief(user_id)
        return result.get("briefing", "Briefing unavailable")
    
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
        """Process a document upload with PDF analysis."""
        db = self._get_db_session()
        try:
            self._initialize_services(db)
            
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
            
            # Download and process document
            # Note: In production, you would download the file using Telegram Bot API
            # For now, return a message indicating the document was received
            return f"📄 Document received: {document.file_name}\n\nTo analyze this document, please ensure the file download is implemented. The document has been saved to your history with ID: {doc.id}."
            
        finally:
            db.close()
    
    async def process_document_with_text(self, user_id: int, document_text: str, document_name: str = "uploaded_document") -> str:
        """Process document text directly (for testing or when text is already extracted)."""
        db = self._get_db_session()
        try:
            self._initialize_services(db)
            
            user_repo = UserRepository(db)
            document_repo = DocumentRepository(db)
            
            user = user_repo.get_by_telegram_id(user_id)
            
            # Create document record
            doc = document_repo.create_document(
                user_id=user.id,
                file_type="text",
                file_id="manual_upload",
                file_name=document_name,
                file_size=len(document_text)
            )
            
            # Analyze document
            document_id = f"{user_id}_active"
            analysis_result = await self.document_agent.analyze_financial_document(
                document_text=document_text,
                document_type="financial_report",
                document_id=document_id
            )
            
            if analysis_result.get("available"):
                return self.response_formatter.format_response(
                    content=analysis_result["analysis"],
                    intent="document_analysis",
                    include_emoji=True
                )
            
            return "Document analysis failed. Please try again."
            
        finally:
            db.close()
    
    async def process_image(self, user_id: int, photo, description: Optional[str] = None) -> str:
        """Process an image upload with chart analysis."""
        db = self._get_db_session()
        try:
            self._initialize_services(db)
            
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
            
            # Analyze image if description provided
            if description:
                analysis_result = await self.image_service.analyze_financial_image(
                    image_file=None,  # Would be the actual file in production
                    ai_provider=self.ai_provider,
                    image_description=description
                )
                
                if analysis_result.get("available"):
                    return self.response_formatter.format_response(
                        content=analysis_result["analysis"],
                        intent="image_analysis",
                        include_emoji=True
                    )
            
            return "🖼️ Image received. For chart analysis, please provide a description of what the image shows. The image has been saved to your history."
            
        finally:
            db.close()
    
    async def process_voice(self, user_id: int, voice) -> str:
        """Process a voice message with speech-to-text."""
        db = self._get_db_session()
        try:
            user_repo = UserRepository(db)
            
            user = user_repo.get_by_telegram_id(user_id)
            
            # Note: Voice transcription requires speech-to-text API integration
            # This is a placeholder that would need real STT implementation
            return "🎤 Voice message received. Voice-to-text processing requires speech-to-text API integration (e.g., OpenAI Whisper). Please use text messages for now."
            
        finally:
            db.close()
    
    async def schedule_user_alerts(self, user_id: int):
        """Schedule background jobs for a user's alerts."""
        db = self._get_db_session()
        try:
            self._initialize_services(db)
            
            # Start background worker if not running
            if not self.background_worker.is_running:
                self.background_worker.start()
            
            # Schedule alert checks
            self.background_worker.schedule_alert_checks(
                alert_service=self.alert_service,
                user_id=user_id,
                interval_minutes=15
            )
            
            # Schedule daily briefings
            self.background_worker.schedule_daily_briefings(
                daily_intelligence_service=self.daily_intelligence_service,
                user_id=user_id,
                morning_time="08:00",
                evening_time="18:00"
            )
            
            return "Background jobs scheduled for alerts and daily briefings."
            
        finally:
            db.close()
    
    async def unschedule_user_jobs(self, user_id: int):
        """Unschedule background jobs for a user."""
        self.background_worker.unschedule_user_jobs(user_id)
        return "Background jobs unscheduled."
