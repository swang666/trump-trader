# Trump Truth Social Trading Monitor

An automated system that monitors Trump's Truth Social posts from trumpstruth.org and generates stock trading ideas based on real-time AI analysis.

## Features

- 🔄 **Real-time monitoring** of Truth Social posts
- 🤖 **Google Gemini AI** powered analysis (FREE)
- 📊 **Sentiment analysis** and NLP processing
- 🏢 **Entity extraction** (companies, sectors, topics)
- 💡 **Automated trading ideas** with confidence levels
- 💾 **Historical data** storage and tracking
- 🎯 **Risk assessment** for each trading idea
- ✉️ **Email notifications** with beautiful HTML reports

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Download spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

3. Create a `.env` file with your API keys:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your free Google Gemini API key at: https://makersuite.google.com/app/apikey

## 📚 Documentation

Complete documentation is available in the [docs/](docs/) folder:

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Gemini API Setup](docs/GEMINI_SETUP.md)** - Setup Google Gemini AI
- **[Production Deployment](docs/DEPLOYMENT_GCE.md)** - Deploy to Google Cloud
- **[Usage Guide](docs/USAGE.md)** - Detailed usage instructions
- **[Production Features](docs/PRODUCTION_READY.md)** - Feature overview
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Codebase organization

**→ See [docs/README.md](docs/README.md) for the complete documentation index**

## Quick Start

```bash
# Run all tests
python run_tests.py

# Or run individual tests
python tests/test_gemini.py           # Test Gemini API
python tests/test_email.py            # Test email notifications
python tests/test_ai_analysis.py      # Test AI analysis
python tests/test_duplicate_prevention.py  # Test duplicate prevention
python tests/test_system.py           # Test full system

# Start monitoring
python main.py
# OR
run.bat     # Windows
./run.sh    # Linux/Mac
```

## Usage

The system will:
1. Monitor trumpstruth.org for new posts every 60 seconds
2. **Skip empty or very short posts** (< 2 characters)
3. Analyze each post using NLP and Google Gemini AI
4. Extract companies, sectors, and sentiment
5. Generate actionable trading ideas with confidence levels
6. **Send email notifications ONLY for significant posts:**
   - Market relevance ≥ 0.3
   - Companies mentioned OR trading ideas generated OR high urgency
   - Substantial content (≥ 2 characters)
7. Save all results to `data/trading_ideas.json`

## Project Structure

```
trump_trader/
├── main.py                  # Main application entry point
├── scraper.py              # Truth Social post scraper
├── analyzer.py             # AI-powered post analysis
├── trading_ideas.py        # Trading idea generator
├── email_notifier.py       # Email notification system
├── run_tests.py            # Test runner
├── tests/                  # Test suite
│   ├── test_gemini.py      # - Test Gemini API
│   ├── test_email.py       # - Test email notifications
│   ├── test_ai_analysis.py # - Test AI analysis
│   └── test_system.py      # - Test full system
├── data/                   # Data storage directory
│   ├── trading_ideas.json
│   ├── post_analysis.json
│   └── monitor_state.json
└── docs/                   # Documentation
    ├── README.md           # Documentation index
    ├── QUICKSTART.md
    ├── GEMINI_SETUP.md
    ├── DEPLOYMENT_GCE.md
    ├── USAGE.md
    ├── PRODUCTION_READY.md
    └── PROJECT_STRUCTURE.md
```

## Production Deployment

For production deployment on Google Compute Engine:

1. Follow the [GCE Deployment Guide](docs/DEPLOYMENT_GCE.md)
2. Configure email notifications in `.env`
3. Run as a systemd service for 24/7 operation
4. Monitor logs and receive email alerts

**Cost:** $0-7/month (can run on Google Cloud free tier!)

## Example Output

```
[2025-10-13 10:30:45] Checking for new posts...
Found 1 new post(s)!

================================================================================
NEW POST DETECTED at 2025-10-13T10:30:00
================================================================================
Content: Great meeting with Tim Cook today! Apple bringing iPhone production to USA!

📊 Analyzing post...
Sentiment: POSITIVE (polarity: 0.85)
Market Relevance: 0.90
Companies: Apple (AAPL)

🤖 AI Insights:
   Strong policy support for domestic manufacturing suggests potential upside
   for AAPL. Reshoring production narrative could drive investor interest...

💡 TRADING IDEAS (2 ideas)

1. Buy AAPL (Apple)
   Confidence: HIGH | Risk: MEDIUM
   Timeframe: short-term
   Rationale: Positive mention of bringing iPhone manufacturing to USA...
```

## Disclaimer

This tool is for educational and research purposes only. Always conduct your own research and consult with financial advisors before making trading decisions.

**Not financial advice. Trade at your own risk.**

## License

This project is for personal and educational use.

---

**📈 Happy Trading! 🤖**
