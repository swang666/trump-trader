# Project Structure

## Organized Directory Layout

```
trump_trader/
├── Core Application Files
│   ├── main.py                     # Main monitoring application
│   ├── scraper.py                  # Truth Social post scraper
│   ├── analyzer.py                 # AI-powered post analysis
│   ├── trading_ideas.py            # Trading idea generator
│   └── email_notifier.py           # Email notification system
│
├── Test Suite (tests/)
│   ├── __init__.py                 # Makes tests a package
│   ├── README.md                   # Test documentation
│   ├── test_gemini.py              # Test Gemini API connection
│   ├── test_email.py               # Test email notifications
│   ├── test_ai_analysis.py         # Test AI analysis pipeline
│   └── test_system.py              # Test full system integration
│
├── Quick Start Scripts
│   ├── run.bat                     # Windows: Start monitor
│   ├── run.sh                      # Linux/Mac: Start monitor
│   ├── run_tests.py                # Run all tests
│   ├── install.bat                 # Windows: Install dependencies
│   └── install.sh                  # Linux/Mac: Install dependencies
│
├── Configuration
│   ├── .env                        # Environment variables (create from .env.example)
│   ├── requirements.txt            # Python dependencies
│   └── .gitignore                  # Git ignore rules
│
├── Documentation
│   ├── README.md                   # Project overview
│   ├── QUICKSTART.md              # 5-minute setup guide
│   ├── USAGE.md                   # Detailed usage instructions
│   ├── GEMINI_SETUP.md            # Gemini API setup guide
│   ├── DEPLOYMENT_GCE.md          # Google Cloud deployment
│   ├── PRODUCTION_READY.md        # Production features summary
│   └── PROJECT_STRUCTURE.md       # This file
│
└── Data Storage (data/)
    ├── trading_ideas.json          # All generated trading ideas
    ├── post_analysis.json          # Detailed post analyses
    ├── monitor_state.json          # Monitor state (processed posts)
    └── .gitkeep                    # Keeps directory in git
```

## File Descriptions

### Core Application

#### `main.py`
Main entry point for the monitoring application.
- Orchestrates all components
- Manages monitoring loop
- Handles state persistence
- Sends email notifications
- **Run with:** `python main.py`

#### `scraper.py`
Fetches posts from Trump Truth Social.
- Monitors trumpstruth.org
- Supports RSS and web scraping
- Tracks last seen post
- Returns new posts only

#### `analyzer.py`
AI-powered post analysis engine.
- Uses Google Gemini AI
- Detects ANY company (not hardcoded)
- Identifies sectors and topics
- Sentiment analysis
- Generates insights and risk factors
- **NO keyword limitations!**

#### `trading_ideas.py`
Generates actionable trading ideas.
- Based on AI analysis
- Provides stock tickers
- Confidence levels (high/medium/low)
- Risk assessment
- Timeframe recommendations

#### `email_notifier.py`
Email notification system.
- Beautiful HTML emails
- Professional formatting
- Includes all analysis details
- Configurable via .env
- Supports Gmail and custom SMTP

### Test Suite (`tests/`)

#### `test_gemini.py`
Tests Gemini API connectivity.
- Verifies API key
- Tests model access
- Sample analysis
- **Run:** `python tests/test_gemini.py`

#### `test_email.py`
Tests email notifications.
- Sends real test email
- Verifies SMTP configuration
- Tests HTML formatting
- **Run:** `python tests/test_email.py`

#### `test_ai_analysis.py`
Tests AI analysis pipeline.
- Full post analysis
- Company detection
- Trading idea generation
- **Run:** `python tests/test_ai_analysis.py`

#### `test_system.py`
Tests full system integration.
- Scraping
- Analysis
- Trading ideas
- End-to-end flow
- **Run:** `python tests/test_system.py`

### Quick Start Scripts

#### `run_tests.py`
Runs all tests in sequence.
- Organized output
- Test summary
- **Run:** `python run_tests.py`

#### `run.bat` / `run.sh`
Quick-start monitor scripts.
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

#### `install.bat` / `install.sh`
Automated dependency installation.
- Installs Python packages
- Downloads spaCy model
- Setup instructions

### Configuration Files

#### `.env`
Environment variables (create from `.env.example`).
```bash
GEMINI_API_KEY=your_key_here
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAIL=alerts@email.com
CHECK_INTERVAL_SECONDS=60
```

#### `requirements.txt`
Python dependencies.
- google-generativeai (Gemini AI)
- requests, beautifulsoup4 (scraping)
- spacy, textblob (NLP)
- etc.

### Documentation

#### `README.md`
Project overview and quick start.

#### `QUICKSTART.md`
5-minute setup guide for beginners.

#### `USAGE.md`
Detailed usage instructions and examples.

#### `GEMINI_SETUP.md`
Complete Gemini API setup guide.

#### `DEPLOYMENT_GCE.md`
Google Compute Engine deployment guide.
- Step-by-step instructions
- Systemd service setup
- Cost estimates
- Troubleshooting

#### `PRODUCTION_READY.md`
Production features summary.
- Email notifications
- Duplicate prevention
- State management
- Feature comparison

### Data Storage (`data/`)

#### `trading_ideas.json`
All generated trading ideas.
```json
[
  {
    "ticker": "AAPL",
    "action": "Buy",
    "confidence": "high",
    "rationale": "...",
    "timestamp": "2025-10-13T10:30:00"
  }
]
```

#### `post_analysis.json`
Detailed analyses of all posts.
```json
[
  {
    "post_id": "...",
    "sentiment": {...},
    "companies": [...],
    "ai_insights": "...",
    "market_relevance": 0.85
  }
]
```

#### `monitor_state.json`
Monitor state for duplicate prevention.
```json
{
  "last_post_id": "...",
  "processed_posts": ["id1", "id2", ...],
  "total_processed": 42
}
```

## Usage Patterns

### Development
```bash
# Test individual components
python tests/test_gemini.py
python tests/test_email.py
python tests/test_ai_analysis.py

# Run all tests
python run_tests.py

# Start monitor locally
python main.py
```

### Production (GCE)
```bash
# Deploy as systemd service
sudo systemctl start trump-trader
sudo systemctl status trump-trader

# View logs
tail -f ~/trump_trader/logs/output.log

# Update code
git pull
sudo systemctl restart trump-trader
```

## Navigation Tips

- **Getting Started?** → Start with `README.md`
- **Quick Setup?** → Follow `QUICKSTART.md`
- **Testing?** → Check `tests/README.md`
- **Deploying?** → Read `DEPLOYMENT_GCE.md`
- **Email Setup?** → See `GEMINI_SETUP.md`
- **Troubleshooting?** → Check relevant test files

## Best Practices

1. **Always test before deploying**
   ```bash
   python run_tests.py
   ```

2. **Keep `.env` secure**
   - Never commit to git
   - Use strong passwords
   - Backup safely

3. **Monitor logs in production**
   ```bash
   tail -f logs/output.log
   ```

4. **Update regularly**
   ```bash
   git pull
   pip install -r requirements.txt
   ```

5. **Backup data periodically**
   ```bash
   tar -czf backup.tar.gz data/
   ```

## Clean and Organized! ✨

All test files are now in `tests/` directory, making the project structure professional and maintainable.

