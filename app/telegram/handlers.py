from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from app.services.bot_service import BotService
from app.config.settings import get_settings
from app.utils.security import validate_text_input, validate_file_size, validate_file_type, sanitize_filename, detect_prompt_injection, validate_stock_symbol
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize bot_service lazily to avoid early settings initialization
_bot_service = None

def get_bot_service():
    """Get or create the bot service instance."""
    global _bot_service
    if _bot_service is None:
        _bot_service = BotService()
    return _bot_service


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    
    welcome_message = f"""👋 Welcome to ATLAS, {user.first_name}!

I'm your AI-powered Financial Assistant. I can help you with:

📊 Stock Analysis
📰 Market Updates
📈 Portfolio Insights
📄 Document Analysis
⏰ Price Alerts

How can I assist you today?"""
    
    keyboard = [
        [InlineKeyboardButton("📊 Analyze Stock", callback_data="analyze_stock")],
        [InlineKeyboardButton("📰 Market Overview", callback_data="market_overview")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    # Initialize user in database
    await get_bot_service().initialize_user(user.id, user.username, user.first_name, user.last_name)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = """🤖 ATLAS Commands:

/start - Start the bot
/help - Show this help message
/analyze <symbol> - Analyze a stock
/watchlist - Manage your watchlist
/alerts - Manage price alerts
/settings - Configure preferences
/history - View conversation history

💡 You can also:
- Send me text messages for financial queries
- Upload PDF documents for analysis
- Share images of charts
- Send voice messages

I'll understand the context and provide relevant insights!"""
    
    await update.message.reply_text(help_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages from users."""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Validate input
    is_valid, error = validate_text_input(message_text)
    if not is_valid:
        await update.message.reply_text(f"⚠️ {error}")
        return
    
    # Check for prompt injection
    is_suspicious, reason = detect_prompt_injection(message_text)
    if is_suspicious:
        logger.warning(f"Prompt injection attempt by user {user_id}: {reason}")
        await update.message.reply_text("I'm sorry, I cannot process that request.")
        return
    
    # Send typing indicator
    await update.message.chat.send_action("typing")
    
    # Process the message through bot service
    response = await get_bot_service().process_text_message(user_id, message_text)
    
    await update.message.reply_text(response)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document uploads (PDFs)."""
    user_id = update.effective_user.id
    document = update.message.document
    
    # Validate file size
    is_valid, error = validate_file_size(document.file_size)
    if not is_valid:
        await update.message.reply_text(f"⚠️ {error}")
        return
    
    # Validate file type
    is_valid, error = validate_file_type(document.file_name, document.mime_type)
    if not is_valid:
        await update.message.reply_text(f"⚠️ {error}")
        return
    
    # Sanitize filename
    safe_filename = sanitize_filename(document.file_name)
    
    # Send typing indicator
    await update.message.chat.send_action("typing")
    
    # Process the document
    response = await bot_service.process_document(user_id, document)
    
    await update.message.reply_text(response)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle image uploads."""
    user_id = update.effective_user.id
    photo = update.message.photo[-1]  # Get largest photo
    
    # Send typing indicator
    await update.message.chat.send_action("typing")
    
    # Process the image
    response = await bot_service.process_image(user_id, photo)
    
    await update.message.reply_text(response)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    user_id = update.effective_user.id
    voice = update.message.voice
    
    # Send typing indicator
    await update.message.chat.send_action("typing")
    
    # Process the voice message
    response = await get_bot_service().process_voice(user_id, voice)
    
    await update.message.reply_text(response)


async def analyze_stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /analyze command."""
    if not context.args or len(context.args) == 0:
        await update.message.reply_text("Please provide a stock symbol. Example: /analyze AAPL")
        return
    
    symbol = context.args[0]
    user_id = update.effective_user.id
    
    # Validate stock symbol
    is_valid, error = validate_stock_symbol(symbol)
    if not is_valid:
        await update.message.reply_text(f"⚠️ {error}")
        return
    
    await update.message.chat.send_action("typing")
    
    response = await get_bot_service().analyze_stock(user_id, symbol)
    await update.message.reply_text(response)


async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /watchlist command."""
    user_id = update.effective_user.id
    
    await update.message.chat.send_action("typing")
    
    response = await get_bot_service().get_watchlist(user_id)
    await update.message.reply_text(response)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command."""
    keyboard = [
        [InlineKeyboardButton("🔔 Notifications", callback_data="notif_settings")],
        [InlineKeyboardButton("💭 Response Style", callback_data="style_settings")],
        [InlineKeyboardButton("🏷️ Investment Profile", callback_data="profile_settings")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("⚙️ Settings", reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    callback_data = query.data
    
    if callback_data == "analyze_stock":
        await query.edit_message_text("Please send the stock symbol you want to analyze.")
    elif callback_data == "market_overview":
        await query.message.chat.send_action("typing")
        response = await get_bot_service().get_market_overview(user_id)
        await query.edit_message_text(response)
    elif callback_data == "settings":
        keyboard = [
            [InlineKeyboardButton("🔔 Notifications", callback_data="notif_settings")],
            [InlineKeyboardButton("💭 Response Style", callback_data="style_settings")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("⚙️ Settings", reply_markup=reply_markup)
    else:
        await query.edit_message_text("Feature coming soon!")


def get_handlers():
    """Return all bot handlers."""
    return [
        CommandHandler("start", start),
        CommandHandler("help", help_command),
        CommandHandler("analyze", analyze_stock_command),
        CommandHandler("watchlist", watchlist_command),
        CommandHandler("settings", settings_command),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
        MessageHandler(filters.Document.PDF, handle_document),
        MessageHandler(filters.PHOTO, handle_photo),
        MessageHandler(filters.VOICE, handle_voice),
    ]
