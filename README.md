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
- **Production Ready**: Webhook mode, security hardening, comprehensive logging
- **AI Safety**: Financial response validation and safety disclaimers

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI
- **Telegram Bot**: python-telegram-bot (webhook + polling support)
- **Database**: SQLAlchemy with SQLite/PostgreSQL support
- **AI Providers**: OpenAI, Anthropic, Google Generative AI
- **Scheduling**: APScheduler for notifications
- **Async**: httpx, aiofiles
- **Logging**: Loguru with secret filtering
- **Security**: Input validation, file upload limits, prompt injection detection

## 📂 Project Structure

```
atlas-—-ai-financial-assistant/
├── app/
│   ├── main.py                 # FastAPI application entry point with startup validation
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
│   │   ├── handlers.py         # Message and command handlers with security
│   │   ├── webhook.py          # Webhook mode support
│   │   └── middleware.py       # Error handling and rate limiting
│   ├── ai/
│   │   ├── providers/
│   │   │   ├── base_provider.py    # AI provider interface
│   │   │   ├── openai_provider.py  # OpenAI implementation
│   │   │   ├── anthropic_provider.py # Anthropic implementation
│   │   │   └── google_provider.py   # Google AI implementation
│   │   ├── agents/
│   │   │   ├── conversation_agent.py # Conversation handling
│   │   │   ├── finance_agent.py     # Financial analysis with safety
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
│       ├── logger.py           # Production logging with secret filtering
│       ├── security.py         # Input validation and file security
│       └── ai_safety.py        # Financial response safety validation
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD pipeline
├── .env.example                # Environment variables template
├── runtime.txt                 # Python version specification (3.12)
├── requirements.txt            # Python dependencies (Python 3.12 compatible)
├── Dockerfile                  # Docker configuration with health check
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
   APP_ENV=development
   WEBHOOK_MODE=false
   ```

5. **Run the application**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

   The bot will start automatically and connect to Telegram using polling mode.

## 🤖 Telegram Commands

- `/start` - Start the bot and see welcome message
- `/help` - Display available commands
- `/analyze <symbol>` - Analyze a stock (e.g., `/analyze AAPL`)
- `/watchlist` - View your watchlist
- `/settings` - Configure preferences

You can also:
- Send text messages for financial queries
- Upload PDF documents for analysis
- Share images of charts
- Send voice messages

## 🔧 Configuration

### Environment Variables

Required variables:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
AI_PROVIDER=openai  # or anthropic, google
OPENAI_API_KEY=your_openai_api_key  # if using OpenAI
DATABASE_URL=sqlite:///./atlas.db
```

Optional variables:
```env
# Webhook Configuration (for production)
WEBHOOK_MODE=false
WEBHOOK_URL=https://your-app.onrender.com
WEBHOOK_SECRET=your_webhook_secret

# Application
APP_ENV=development
LOG_LEVEL=INFO
MAX_CONVERSATION_HISTORY=50

# Security
MAX_FILE_SIZE_MB=20
ALLOWED_FILE_TYPES=pdf,png,jpg,jpeg
RATE_LIMIT_PER_MINUTE=30

# Financial APIs (Optional)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
POLYGON_API_KEY=your_polygon_api_key
```

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

By default, ATLAS uses SQLite for development. For production, use PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@host:port/database
```

## ☁️ Deployment

### Render Deployment

ATLAS is configured for automatic deployment to Render using the provided `render.yaml` configuration file.

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Health Check Path:**
```
/health
```

#### Manual Render Deployment Steps:

1. **Push code to GitHub**:
   ```bash
   git add .
   git commit -m "Production ready deployment"
   git push origin main
   ```

2. **Create Render Web Service**:
   - Go to [render.com](https://render.com)
   - Create a new Web Service
   - Connect your GitHub repository: `https://github.com/Sreevalli20/telegram.git`
   - Render will automatically detect the `render.yaml` configuration
   - The service will be named: `atlas-ai-financial-assistant`

3. **Configure Environment Variables** in Render dashboard:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   AI_PROVIDER=openai
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key (if using Anthropic)
   GOOGLE_API_KEY=your_google_api_key (if using Google)
   WEBHOOK_MODE=true
   WEBHOOK_URL=https://your-app.onrender.com
   WEBHOOK_SECRET=your_webhook_secret
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key (optional)
   POLYGON_API_KEY=your_polygon_api_key (optional)
   ```

   **Note:** The following environment variables are automatically set by `render.yaml`:
   - `APP_ENV=production`
   - `LOG_LEVEL=INFO`
   - `MAX_CONVERSATION_HISTORY=50`
   - `RENDER=true`
   - `PYTHONUNBUFFERED=1`

4. **Deploy** - Render will automatically build and deploy

5. **Set Telegram Webhook** (if not auto-configured):
   ```bash
   curl -F "url=https://your-app.onrender.com/telegram/webhook" \
   -F "secret_token=your_webhook_secret" \
   https://api.telegram.org/botYOUR_TOKEN/setWebhook
   ```

#### Database Persistence on Render

The application automatically configures SQLite database storage for Render production:
- Database path: `/opt/render/project/data/atlas.db`
- The data directory is automatically created on startup
- Render's persistent storage ensures the database survives deployments

#### Important Notes for Render Deployment

- **No Frontend**: This is a pure backend Telegram bot application. There is no frontend to deploy to Vercel.
- **Webhook Mode**: Production deployment uses webhook mode for better performance
- **Port Configuration**: The application automatically uses the `$PORT` environment variable provided by Render
- **Health Checks**: Render will monitor the `/health` endpoint to ensure the service is running
- **Database**: SQLite is used with Render's persistent storage for database persistence

### Docker Deployment

```bash
# Build the image
docker build -t atlas-bot .

# Run the container
docker run -p 8000:8000 \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e AI_PROVIDER=openai \
  -e OPENAI_API_KEY=your_key \
  -e DATABASE_URL=sqlite:///./data/atlas.db \
  -e WEBHOOK_MODE=false \
  -e PORT=8000 \
  atlas-bot
```

**Docker Health Check:**
The Dockerfile includes a health check that monitors the `/health` endpoint every 30 seconds.

### Docker Compose

```yaml
version: '3.8'
services:
  atlas:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - AI_PROVIDER=${AI_PROVIDER}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=sqlite:///./data/atlas.db
      - WEBHOOK_MODE=false
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

## � Security Features

- **Input Validation**: All user inputs are validated for length and dangerous patterns
- **File Upload Security**: File size limits, type validation, and filename sanitization
- **Prompt Injection Detection**: Detects and blocks potential prompt injection attempts
- **Rate Limiting**: Configurable rate limits per user to prevent abuse
- **Secret Filtering**: Logs automatically filter out API keys and sensitive data
- **Webhook Security**: Optional secret token validation for webhook endpoints
- **AI Safety**: Financial responses include safety disclaimers and avoid guaranteed returns

## �📊 Database Models

- **User**: Telegram user information and profile
- **Conversation**: Chat sessions with users
- **Message**: Individual messages in conversations
- **CompanyWatchlist**: User's tracked companies
- **ResearchHistory**: Research queries and results
- **Document**: Uploaded documents and analysis
- **Preference**: User settings and preferences
- **Notification**: Alerts and notifications

## 🧪 Testing

Run tests with:
```bash
python -m pytest tests/ -v
```

Run code formatting check:
```bash
black --check app/
```

Run security scan:
```bash
bandit -r app/
```

## 📝 Architecture

### Application Flow

1. **Telegram → FastAPI**: Messages received via webhook or polling
2. **FastAPI → Handlers**: Request routed to appropriate handler
3. **Handlers → Bot Service**: Business logic processing
4. **Bot Service → AI Agents**: AI-powered analysis
5. **AI Agents → External APIs**: Financial data retrieval
6. **Response → Telegram**: Formatted response sent back

### Webhook vs Polling

- **Development**: Uses polling mode (`WEBHOOK_MODE=false`)
- **Production**: Uses webhook mode (`WEBHOOK_MODE=true`) for better performance

## 🆘 Troubleshooting

### Bot doesn't respond
- Check TELEGRAM_BOT_TOKEN is correct
- Verify AI provider API key is valid
- Check logs for error messages
- Ensure webhook is properly configured in production
- Verify the health check endpoint is accessible: `https://your-app.onrender.com/health`

### Database errors
- Ensure DATABASE_URL is correct
- Check database file permissions
- Verify SQLAlchemy connection
- For PostgreSQL, ensure database exists

### AI provider errors
- Verify API key is valid
- Check API quota/credits
- Ensure provider is selected in config
- Check network connectivity

### Deployment issues
- Verify Python 3.12 is being used
- Check all environment variables are set
- Review Render logs for build errors
- Ensure webhook URL is accessible

### Webhook not working
- Verify WEBHOOK_MODE is set to true
- Check WEBHOOK_URL is correct and accessible
- Ensure WEBHOOK_SECRET matches between config and Telegram
- Check firewall/security settings

## 🔍 Monitoring

### Health Check Endpoint

```bash
curl https://your-app.onrender.com/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Bot Status Endpoint

```bash
curl https://your-app.onrender.com/bot/status
```

Response:
```json
{
  "status": "running",
  "bot_id": 123456789,
  "mode": "webhook"
}
```

### Logs

Logs are stored in the `logs/` directory:
- `atlas.log` - General application logs
- `errors.log` - Error-specific logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📝 License

This project is part of a hackathon submission.

## 🚀 Future Improvements

- [ ] Add more financial data providers
- [ ] Implement advanced technical analysis
- [ ] Add portfolio tracking features
- [ ] Support for more document types
- [ ] Multi-language support
- [ ] Advanced user analytics
- [ ] Integration with trading platforms

## 📞 Support

For issues or questions, please open an issue on GitHub.
