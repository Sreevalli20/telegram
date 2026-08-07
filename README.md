# ATLAS - AI Financial Assistant

An AI-powered Financial Assistant that lives completely inside Telegram. ATLAS provides professional financial analysis, stock research, market insights, and document analysis through a conversational interface.

## 🚀 Features

- **Conversational AI**: Natural language interface for financial queries
- **Stock Analysis**: Comprehensive stock analysis with AI-powered insights
- **Market Overview**: Real-time market trends and sector analysis
- **Document Analysis**: Upload and analyze financial documents (PDFs)
- **Watchlist Management**: Track companies and set price alerts
- **Personalized Memory**: Learns user preferences and investment interests
- **Multi-Provider AI**: Support for OpenAI, Anthropic, and Google AI
- **Async Architecture**: Built with FastAPI and async/await patterns

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI
- **Telegram Bot**: python-telegram-bot
- **Database**: SQLAlchemy with SQLite/PostgreSQL support
- **AI Providers**: OpenAI, Anthropic, Google Generative AI
- **Scheduling**: APScheduler for notifications
- **Async**: httpx, aiofiles

## 📂 Project Structure

```
atlas-—-ai-financial-assistant/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   └── settings.py         # Configuration and environment variables
│   ├── database/
│   ├── models/
│   │   ├── user.py             # User model
│   │   ├── conversation.py    # Conversation model
│   │   ├── message.py          # Message model
│   │   ├── watchlist.py        # Company watchlist model
│   │   ├── research.py         # Research history model
│   │   ├── document.py         # Document model
│   │   ├── preference.py       # User preferences model
│   │   └── notification.py     # Notification model
│   ├── repositories/
│   │   ├── base_repository.py  # Base repository with CRUD operations
│   │   ├── user_repository.py
│   │   ├── conversation_repository.py
│   │   ├── message_repository.py
│   │   ├── watchlist_repository.py
│   │   ├── research_repository.py
│   │   ├── document_repository.py
│   │   ├── preference_repository.py
│   │   └── notification_repository.py
│   ├── services/
│   │   └── bot_service.py      # Core bot business logic
│   ├── telegram/
│   │   ├── bot.py              # Telegram bot configuration
│   │   └── handlers.py         # Message and command handlers
│   ├── ai/
│   │   ├── providers/
│   │   │   ├── base_provider.py    # AI provider interface
│   │   │   ├── openai_provider.py  # OpenAI implementation
│   │   │   ├── anthropic_provider.py # Anthropic implementation
│   │   │   └── google_provider.py   # Google AI implementation
│   │   ├── agents/
│   │   │   ├── conversation_agent.py # Conversation handling
│   │   │   ├── finance_agent.py     # Financial analysis
│   │   │   ├── document_agent.py   # Document processing
│   │   │   ├── memory_agent.py     # User memory management
│   │   │   └── notification_agent.py # Notification generation
│   │   ├── prompts/
│   │   ├── memory/
│   │   └── tools/
│   ├── finance/
│   ├── documents/
│   ├── scheduler/
│   │   └── scheduler.py        # Notification scheduler
│   └── utils/
│       └── logger.py           # Logging configuration
├── .env.example                # Environment variables template
├── runtime.txt                 # Python version specification
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── render.yaml                 # Render deployment config
└── README.md                   # This file
```

## ⚙️ Setup Instructions

### Prerequisites

- **Python 3.12** (Required for Render compatibility)
- Python 3.14 is not currently supported due to dependency limitations
- Telegram Bot Token (obtain from @BotFather)
- AI Provider API Key (OpenAI, Anthropic, or Google)

**Note**: If your local machine has Python 3.14, you will need to install Python 3.12 to run this locally. The project is configured for Python 3.12 to ensure Render deployment compatibility.

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sreevalli20/telegram.git
   cd atlas-—-ai-financial-assistant
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   AI_PROVIDER=openai
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=sqlite:///./atlas.db
   ```

5. **Run the application**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

   The bot will start automatically and connect to Telegram.

## 🤖 Telegram Commands

- `/start` - Start the bot and see welcome message
- `/help` - Display available commands
- `/analyze <symbol>` - Analyze a stock (e.g., `/analyze AAPL`)
- `/watchlist` - View your watchlist
- `/settings` - Configure preferences

## 🔧 Configuration

### AI Providers

ATLAS supports multiple AI providers. Configure in `.env`:

```env
# Choose your provider: openai, anthropic, or google
AI_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key

# Google
GOOGLE_API_KEY=your_google_api_key
```

### Database

By default, ATLAS uses SQLite. For production, use PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@host:port/database
```

## ☁️ Deployment

### Render

1. Push code to GitHub
2. Create a new Web Service on Render
3. Connect your repository
4. Add environment variables in Render dashboard
5. Deploy

Render will automatically detect the `runtime.txt` and `requirements.txt` files.

### Docker

```bash
docker build -t atlas-bot .
docker run -p 8000:8000 --env-file .env atlas-bot
```

## 📊 Database Models

- **User**: Telegram user information and profile
- **Conversation**: Chat sessions with users
- **Message**: Individual messages in conversations
- **CompanyWatchlist**: User's tracked companies
- **ResearchHistory**: Research queries and results
- **Document**: Uploaded documents and analysis
- **Preference**: User settings and preferences
- **Notification**: Alerts and notifications

## 🔐 Security

- Never commit `.env` file or API keys
- Use environment variables for all sensitive data
- Telegram bot token is required for bot operation
- AI provider API keys are required for AI features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is part of a hackathon submission.

## 🆘 Troubleshooting

### Bot doesn't respond
- Check TELEGRAM_BOT_TOKEN is correct
- Verify AI provider API key is valid
- Check logs for error messages

### Database errors
- Ensure DATABASE_URL is correct
- Check database file permissions
- Verify SQLAlchemy connection

### AI provider errors
- Verify API key is valid
- Check API quota/credits
- Ensure provider is selected in config

## 📞 Support

For issues or questions, please open an issue on GitHub.
