from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import get_db
from app.models.message import MessageType
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
from app.services.watchlist_service import WatchlistService
from app.services.alert_service import AlertService
from app.services.daily_intelligence_service import DailyIntelligenceService
from app.services.voice_service import VoiceService
from app.services.image_service import ImageService
from app.services.explanation_service import ExplanationService
from app.services.response_formatter import ResponseFormatter
from app.workers.background_worker import BackgroundWorker
from app.finance.deterministic_analysis import DeterministicAnalysis
from app.finance.ticker_resolver import TickerResolver
from app.finance.deterministic_knowledge import DeterministicKnowledge


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
        self.deterministic = DeterministicAnalysis()
        self.ticker_resolver = TickerResolver()
        self.deterministic_knowledge = DeterministicKnowledge()
        
        # Initialize services (will be created with DB session when needed)
        self.watchlist_service = None
        self.alert_service = None
        self.daily_intelligence_service = None
        self.voice_service = VoiceService()
        self.image_service = ImageService()
        self.explanation_service = ExplanationService(self.ai_provider)
        
        # Log AI provider status
        if self.ai_provider is None:
            from app.utils.logger import get_logger
            logger = get_logger(__name__)
            logger.info("AI provider not configured. Using deterministic mode for core functionality.")
    
    def _get_ai_provider(self):
        """Get the configured AI provider. Returns None if no API key is available."""
        provider_name = self.settings.ai_provider.lower()
        
        if provider_name == "openai":
            if self.settings.openai_api_key:
                return OpenAIProvider(api_key=self.settings.openai_api_key)
        elif provider_name == "anthropic":
            if self.settings.anthropic_api_key:
                return AnthropicProvider(api_key=self.settings.anthropic_api_key)
        elif provider_name == "google":
            if self.settings.google_api_key:
                return GoogleProvider(api_key=self.settings.google_api_key)
        else:
            raise ValueError(f"Unknown AI provider: {provider_name}")
        
        # No API key available for the configured provider
        return None
    
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
                message_type=MessageType.TEXT
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
            intent_result = await self.intent_detector.detect(message_text)
            intent = intent_result.intent
            entities = intent_result.entities
            
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
            try:
                response = await self._route_intent(
                    intent=intent,
                    entities=entities,
                    message_text=message_text,
                    user_id=user.id,
                    db_user=user,
                    history=history,
                    user_context=user_context
                )
            except RuntimeError as e:
                # Handle AI provider errors gracefully
                from app.utils.logger import get_logger
                logger = get_logger(__name__)
                logger.error(f"AI provider error during intent routing: {str(e)}")
                response = "🤖 I'm having trouble connecting to my AI service right now. Please try again in a moment. The service may be temporarily unavailable."
            
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
        """Route intent to appropriate handler with deterministic-first approach."""
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        
        symbols = entities.get("symbols", [])
        companies = entities.get("companies", [])
        
        # Log intent routing
        logger.info(f"Routing intent={intent}, symbols={symbols}, companies={companies}")
        
        # Handle deterministic intents (no AI required)
        if intent == "greeting":
            return self.deterministic.get_greeting()
        elif intent == "help":
            return self.deterministic.get_help_text()
        
        # Handle explanation intents using deterministic knowledge base
        if intent == "explanation":
            concept = self.deterministic_knowledge.extract_concept(message_text)
            if concept:
                explanation = self.deterministic_knowledge.get_concept_explanation(concept)
                if explanation:
                    return explanation
            # Fallback to AI if available
            if self.ai_provider:
                return await self._handle_explanation(message_text)
            else:
                return self.deterministic.get_help_text()
        
        # Check if intent requires a symbol but none was provided
        if self.ticker_resolver.requires_symbol(intent, entities):
            logger.info(f"Intent {intent} requires symbol but none provided")
            return "📈 Which stock would you like me to analyze? Send a company name or ticker, for example Apple or AAPL."
        
        # Handle stock analysis with deterministic fallback
        if intent == "stock_analysis":
            if symbols:
                return await self._handle_stock_lookup(symbols[0])
            elif companies:
                # Try to resolve company name to ticker
                for company in companies:
                    ticker = self.ticker_resolver.resolve(company)
                    if ticker:
                        return await self._handle_stock_lookup(ticker)
            return "📈 Which stock would you like me to analyze? Send a company name or ticker, for example Apple or AAPL."
        
        # Handle stock lookup (works with or without AI)
        if intent == "stock_lookup" and symbols:
            return await self._handle_stock_lookup(symbols[0])
        
        # Handle market analysis with deterministic fallback
        if intent == "market_analysis":
            return await self._handle_market_analysis_deterministic()
        
        # Handle comparison with deterministic fallback
        if intent == "comparison":
            if len(symbols) >= 2:
                return await self._handle_comparison_deterministic(symbols[:2])
            elif len(companies) >= 2:
                # Resolve companies to tickers
                tickers = []
                for company in companies[:2]:
                    ticker = self.ticker_resolver.resolve(company)
                    if ticker:
                        tickers.append(ticker)
                if len(tickers) >= 2:
                    return await self._handle_comparison_deterministic(tickers)
            return "📊 Which companies would you like me to compare? Send two company names or tickers, for example Apple and Microsoft."
        
        # Handle company research with deterministic fallback
        if intent == "company_research":
            if symbols:
                return await self._handle_company_research_deterministic(symbols[0])
            elif companies:
                for company in companies:
                    ticker = self.ticker_resolver.resolve(company)
                    if ticker:
                        return await self._handle_company_research_deterministic(ticker)
            return "📈 Which company would you like me to research? Send a company name or ticker, for example Apple or AAPL."
        
        # Handle news request (requires AI or fallback)
        if intent == "news_request":
            if self.ai_provider:
                return await self._handle_news_request(symbols[0] if symbols else None)
            else:
                return "📰 News features require AI. Configure GOOGLE_API_KEY for news updates, or try 'market overview' for available market data."
        
        # Handle watchlist (database only, no AI needed)
        if intent == "watchlist":
            return await self._handle_watchlist(entities, user_id)
        
        # Handle alert (database only, no AI needed)
        if intent == "alert":
            return await self._handle_alert(entities, user_id)
        
        # Handle document chat (requires AI)
        if intent == "document_analysis":
            if self.ai_provider:
                return await self._handle_document_chat(message_text, user_id)
            else:
                return "📄 Document analysis requires AI. Configure GOOGLE_API_KEY for document features."
        
        # Handle daily briefing (requires AI or fallback)
        if intent == "briefing":
            if self.ai_provider:
                return await self._handle_daily_briefing(user_id)
            else:
                return "📊 Briefing requires AI. Configure GOOGLE_API_KEY for personalized briefings, or try 'market overview'."
        
        # Handle valuation with deterministic fallback
        if intent == "valuation":
            if symbols:
                return await self._handle_stock_lookup(symbols[0])  # Stock lookup includes valuation
            elif companies:
                for company in companies:
                    ticker = self.ticker_resolver.resolve(company)
                    if ticker:
                        return await self._handle_stock_lookup(ticker)
            return "📈 Which stock would you like me to analyze? Send a company name or ticker."
        
        # Handle financial health with deterministic fallback
        if intent == "financial_health":
            if symbols:
                return await self._handle_stock_lookup(symbols[0])  # Stock lookup includes financial metrics
            elif companies:
                for company in companies:
                    ticker = self.ticker_resolver.resolve(company)
                    if ticker:
                        return await self._handle_stock_lookup(ticker)
            return "📈 Which stock would you like me to analyze? Send a company name or ticker."
        
        # Default to conversation agent if AI available, otherwise use deterministic fallback
        if self.ai_provider:
            try:
                return await self.conversation_agent.process_message(
                    message_text, history, user_context
                )
            except RuntimeError as e:
                logger.error(f"AI provider error during conversation: {str(e)}")
                return self.deterministic.get_unknown_response()
        else:
            # Try to extract and handle finance concepts
            if self.deterministic_knowledge.has_concept(message_text):
                concept = self.deterministic_knowledge.extract_concept(message_text)
                explanation = self.deterministic_knowledge.get_concept_explanation(concept)
                if explanation:
                    return explanation
            
            return self.deterministic.get_unknown_response()
    
    async def _handle_stock_lookup(self, symbol: str) -> str:
        """Handle stock lookup intent."""
        try:
            # The finance_agent now handles AI fallback internally
            result = await self.finance_agent.analyze_stock(symbol)
            if result.get("data", {}).get("stock_price", {}).get("available", True):
                analysis = result.get("analysis", "Analysis unavailable")
                # Add note if not AI enhanced
                if not result.get("ai_enhanced", True):
                    analysis += "\n\n💡 (Data-based analysis - configure GOOGLE_API_KEY for AI-powered insights)"
                return analysis
            return f"Unable to fetch data for {symbol}. Please check the symbol and try again."
        except Exception as e:
            from app.utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Stock lookup error: {str(e)}")
            return f"Error fetching stock data for {symbol}. Please try again later."
    
    async def _handle_company_research(self, symbol: str) -> str:
        """Handle company research intent with AI."""
        if self.ai_provider is None:
            return await self._handle_company_research_deterministic(symbol)
        try:
            result = await self.finance_agent.get_company_research(symbol)
            return result.get("analysis", "Research unavailable")
        except RuntimeError as e:
            from app.utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"AI provider error during company research: {str(e)}")
            return await self._handle_company_research_deterministic(symbol)
    
    async def _handle_company_research_deterministic(self, symbol: str) -> str:
        """Handle company research using deterministic data only."""
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        
        try:
            # Use the same stock lookup but with more context
            result = await self.finance_agent.analyze_stock(symbol)
            stock_price = result.get("data", {}).get("stock_price", {})
            company_overview = result.get("data", {}).get("company_overview", {})
            financial_metrics = result.get("data", {}).get("financial_metrics", {})
            
            if not stock_price.get("available", False):
                return f"Unable to fetch data for {symbol.upper()}. Please check the symbol and try again."
            
            lines = [f"📊 {symbol.upper()} Company Research"]
            lines.append("")
            
            # Company info
            if company_overview.get("company_name"):
                lines.append(f"Company: {company_overview['company_name']}")
            if company_overview.get("industry"):
                lines.append(f"Industry: {company_overview['industry']}")
            if company_overview.get("sector"):
                lines.append(f"Sector: {company_overview['sector']}")
            lines.append("")
            
            # Current price info
            if stock_price.get("current_price"):
                lines.append(f"💰 Current Price: ${stock_price['current_price']:.2f}")
            if stock_price.get("change") is not None:
                change = stock_price['change']
                change_percent = stock_price.get('change_percent', 0)
                if change >= 0:
                    lines.append(f"Change: +${change:.2f} (+{change_percent:.2f}%) 📈")
                else:
                    lines.append(f"Change: ${change:.2f} ({change_percent:.2f}%) 📉")
            lines.append("")
            
            # Market cap
            if stock_price.get("market_cap"):
                market_cap = stock_price['market_cap']
                if market_cap >= 1e12:
                    mc_str = f"${market_cap/1e12:.2f}T"
                elif market_cap >= 1e9:
                    mc_str = f"${market_cap/1e9:.2f}B"
                elif market_cap >= 1e6:
                    mc_str = f"${market_cap/1e6:.2f}M"
                else:
                    mc_str = f"${market_cap:,.0f}"
                lines.append(f"Market Cap: {mc_str}")
            lines.append("")
            
            # Key metrics
            if financial_metrics.get("available"):
                lines.append("📈 Key Metrics:")
                if financial_metrics.get("trailing_pe"):
                    lines.append(f"• P/E Ratio: {financial_metrics['trailing_pe']:.2f}")
                if financial_metrics.get("profit_margin"):
                    lines.append(f"• Profit Margin: {financial_metrics['profit_margin']*100:.2f}%")
                if financial_metrics.get("return_on_equity"):
                    lines.append(f"• ROE: {financial_metrics['return_on_equity']*100:.2f}%")
                if financial_metrics.get("debt_to_equity"):
                    lines.append(f"• Debt-to-Equity: {financial_metrics['debt_to_equity']:.2f}")
                lines.append("")
            
            lines.append("📌 This is data-based company information. For AI-powered research insights, configure GOOGLE_API_KEY.")
            
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Deterministic company research error: {str(e)}")
            return f"Unable to fetch company data for {symbol.upper()}. Please try again later."
    
    async def _handle_market_analysis(self) -> str:
        """Handle market analysis intent with AI."""
        if self.ai_provider is None:
            return await self._handle_market_analysis_deterministic()
        try:
            result = await self.finance_agent.get_market_overview()
            return result.get("analysis", "Market overview unavailable")
        except RuntimeError as e:
            from app.utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"AI provider error during market analysis: {str(e)}")
            return await self._handle_market_analysis_deterministic()
    
    async def _handle_market_analysis_deterministic(self) -> str:
        """Handle market analysis using deterministic data only."""
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        
        try:
            from app.finance import MarketDataService
            market_service = MarketDataService()
            
            lines = ["📊 Market Overview"]
            lines.append("")
            
            # Try to get major indices
            indices = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow, Nasdaq
            index_data = []
            
            for index in indices:
                try:
                    data = await market_service.get_stock_price(index)
                    if data.get("available"):
                        index_data.append(data)
                except Exception as e:
                    logger.warning(f"Failed to fetch {index}: {str(e)}")
            
            if index_data:
                lines.append("📈 Major Indices:")
                for data in index_data:
                    symbol = data.get("symbol", "").replace("^", "")
                    price = data.get("current_price")
                    change = data.get("change")
                    change_percent = data.get("change_percent")
                    
                    if price:
                        lines.append(f"{symbol}: ${price:.2f}")
                        if change is not None:
                            if change >= 0:
                                lines.append(f"  Change: +${change:.2f} (+{change_percent:.2f}%)")
                            else:
                                lines.append(f"  Change: ${change:.2f} ({change_percent:.2f}%)")
                lines.append("")
            
            # Try to get market movers
            try:
                movers = await market_service.get_market_movers("US", limit=3)
                if movers.get("gainers"):
                    lines.append("🔼 Top Gainers:")
                    for gainer in movers["gainers"][:3]:
                        symbol = gainer.get("symbol", "")
                        change = gainer.get("change_percent", 0)
                        lines.append(f"• {symbol}: +{change:.2f}%")
                
                if movers.get("losers"):
                    lines.append("")
                    lines.append("🔽 Top Losers:")
                    for loser in movers["losers"][:3]:
                        symbol = loser.get("symbol", "")
                        change = loser.get("change_percent", 0)
                        lines.append(f"• {symbol}: {change:.2f}%")
            except Exception as e:
                logger.warning(f"Failed to fetch market movers: {str(e)}")
            
            lines.append("")
            lines.append("📌 This is live market data. For AI-powered market analysis, configure GOOGLE_API_KEY.")
            
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Deterministic market analysis error: {str(e)}")
            return "📊 Live market data is temporarily unavailable. Try individual stock lookups like 'AAPL' or 'Apple'."
    
    async def _handle_comparison(self, symbols: list) -> str:
        """Handle comparison intent with AI."""
        if self.ai_provider is None:
            return await self._handle_comparison_deterministic(symbols)
        try:
            result = await self.finance_agent.compare_companies(symbols[0], symbols[1])
            return result.get("comparison_analysis", "Comparison unavailable")
        except RuntimeError as e:
            from app.utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"AI provider error during comparison: {str(e)}")
            return await self._handle_comparison_deterministic(symbols)
    
    async def _handle_comparison_deterministic(self, symbols: list) -> str:
        """Handle comparison using deterministic data only."""
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        
        try:
            from app.finance import MarketDataService
            market_service = MarketDataService()
            
            if len(symbols) < 2:
                return "📊 Please provide at least two symbols to compare."
            
            symbol1, symbol2 = symbols[0], symbols[1]
            
            # Fetch data for both symbols
            data1 = await market_service.get_stock_price(symbol1)
            data2 = await market_service.get_stock_price(symbol2)
            
            if not data1.get("available") or not data2.get("available"):
                return f"Unable to fetch data for comparison. Please check the symbols: {symbol1}, {symbol2}"
            
            lines = [f"⚖️ Comparison: {symbol1.upper()} vs {symbol2.upper()}"]
            lines.append("")
            
            # Create comparison table
            lines.append("| Metric       | {} | {} |".format(symbol1.upper(), symbol2.upper()))
            lines.append("|--------------|-----|-----|")
            
            # Price
            price1 = data1.get("current_price")
            price2 = data2.get("current_price")
            if price1 and price2:
                lines.append(f"| Price        | ${price1:.2f} | ${price2:.2f} |")
            
            # Change
            change1 = data1.get("change_percent")
            change2 = data2.get("change_percent")
            if change1 is not None and change2 is not None:
                lines.append(f"| Day Change   | {change1:+.2f}% | {change2:+.2f}% |")
            
            # Market Cap
            mc1 = data1.get("market_cap")
            mc2 = data2.get("market_cap")
            if mc1 and mc2:
                mc1_str = f"${mc1/1e9:.1f}B" if mc1 >= 1e9 else f"${mc1/1e6:.1f}M"
                mc2_str = f"${mc2/1e9:.1f}B" if mc2 >= 1e9 else f"${mc2/1e6:.1f}M"
                lines.append(f"| Market Cap   | {mc1_str} | {mc2_str} |")
            
            # Volume
            vol1 = data1.get("volume")
            vol2 = data2.get("volume")
            if vol1 and vol2:
                vol1_str = f"{vol1/1e6:.1f}M" if vol1 >= 1e6 else f"{vol1:,.0f}"
                vol2_str = f"{vol2/1e6:.1f}M" if vol2 >= 1e6 else f"{vol2:,.0f}"
                lines.append(f"| Volume       | {vol1_str} | {vol2_str} |")
            
            lines.append("")
            
            # Simple comparison notes
            lines.append("📊 Key Observations:")
            
            if price1 and price2:
                if price1 > price2:
                    lines.append(f"• {symbol1.upper()} trades at ${(price1/price2 - 1)*100:.1f}% higher than {symbol2.upper()}")
                else:
                    lines.append(f"• {symbol2.upper()} trades at ${(price2/price1 - 1)*100:.1f}% higher than {symbol1.upper()}")
            
            if change1 is not None and change2 is not None:
                if change1 > change2:
                    lines.append(f"• {symbol1.upper()} performing better today ({change1:+.2f}% vs {change2:+.2f}%)")
                else:
                    lines.append(f"• {symbol2.upper()} performing better today ({change2:+.2f}% vs {change1:+.2f}%)")
            
            if mc1 and mc2:
                if mc1 > mc2:
                    lines.append(f"• {symbol1.upper()} has larger market cap")
                else:
                    lines.append(f"• {symbol2.upper()} has larger market cap")
            
            lines.append("")
            lines.append("📌 This is data-based comparison. For AI-powered comparative analysis, configure GOOGLE_API_KEY.")
            
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Deterministic comparison error: {str(e)}")
            return f"Error comparing {symbols[0]} and {symbols[1]}. Please try again later."
    
    async def _handle_news_request(self, symbol: Optional[str]) -> str:
        """Handle news request intent."""
        if self.ai_provider is None:
            return "🤖 AI features are not currently configured. Please configure a Google API key (GOOGLE_API_KEY) for free tier access to use this feature."
        try:
            if symbol:
                result = await self.finance_agent.get_financial_news(symbol)
            else:
                result = await self.finance_agent.get_financial_news()
            return result.get("analysis", "News unavailable")
        except RuntimeError as e:
            from app.utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"AI provider error during news request: {str(e)}")
            return "📰 Financial news is temporarily unavailable. Please try again later."
    
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
        # Handle common financial concepts deterministically
        concept_lower = concept.lower()
        if "p/e" in concept_lower or "pe ratio" in concept_lower or "price to earnings" in concept_lower:
            return self.deterministic.explain_pe_ratio()
        elif "dividend" in concept_lower:
            return self.deterministic.explain_dividend()
        elif "market cap" in concept_lower or "market capitalization" in concept_lower:
            return self.deterministic.explain_market_cap()
        
        # Fall back to AI if available
        if self.ai_provider:
            try:
                result = await self.explanation_service.explain_concept(concept)
                return result.get("explanation", "Explanation unavailable")
            except RuntimeError as e:
                from app.utils.logger import get_logger
                logger = get_logger(__name__)
                logger.error(f"AI explanation failed: {str(e)}")
                return "🤖 AI explanation unavailable. Try asking about P/E ratio, dividends, or market cap for deterministic explanations."
        
        return "🤖 This concept requires AI for explanation. Try asking about P/E ratio, dividends, or market cap."
    
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
