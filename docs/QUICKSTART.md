# Quick Start Guide - Trump Truth Social Trading Monitor

## 5-Minute Setup

### Step 1: Install Dependencies (2 minutes)
```bash
# Windows
install.bat

# Linux/Mac
chmod +x install.sh
./install.sh
```

### Step 2: Get FREE Gemini API Key (2 minutes)

1. **Visit:** https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Click** "Create API Key" (or "Get API Key")
4. **Copy** the API key

### Step 3: Configure API Key (1 minute)

Create a file named `.env` in the project folder:

```bash
# Contents of .env file:
GEMINI_API_KEY=paste_your_api_key_here
CHECK_INTERVAL_SECONDS=60
```

### Step 4: Test Gemini API
```bash
python tests/test_gemini.py
```

You should see:
```
✅ SUCCESS! Gemini API is working!

Sample Analysis:
--------------------------------------------------------------------------------
The post displays positive sentiment regarding American manufacturing,
specifically mentioning Tesla and Ford's expansion...
--------------------------------------------------------------------------------
```

### Step 5: Test Full System
```bash
python run_tests.py
# Or test individual components:
python tests/test_gemini.py
python tests/test_email.py  
python tests/test_ai_analysis.py
python tests/test_system.py
```

### Step 6: Start Monitoring
```bash
python main.py
```

## What You'll See

```
================================================================================
TRUMP TRUTH SOCIAL TRADING MONITOR
================================================================================
Monitoring interval: 60 seconds
Press Ctrl+C to stop

✓ Google Gemini AI enabled
Testing connection to trumpstruth.org...
✓ Connection successful

[2025-10-13 10:30:45] Checking for new posts...
Found 1 new post(s)!

================================================================================
NEW POST DETECTED at 2025-10-13T10:30:00
================================================================================
Content: Great news for American energy! We are DRILLING...
Link: https://trumpstruth.org/...

📊 Analyzing post...
Sentiment: POSITIVE (polarity: 0.75)
Market Relevance: 0.80
Companies: ['oil']
Sectors: ['energy']

🤖 Gemini AI Analysis:
   This post signals strong support for domestic energy production.
   Energy sector ETFs like XLE could see increased interest.
   Oil and gas companies may benefit from policy support.
   Consider monitoring XLE, XOP for entry points.

💡 TRADING IDEAS (2 ideas)

================================================================================
TRADING IDEAS (2 ideas)
================================================================================

1. Buy XLE (Energy Sector ETF)
   Type: SECTOR | Confidence: HIGH | Risk: MEDIUM
   Timeframe: short-term
   Rationale: Positive sentiment on energy sector based on post content

2. Buy XOP (Oil & Gas Exploration ETF)
   Type: SECTOR | Confidence: MEDIUM | Risk: MEDIUM
   Timeframe: medium-term
   Rationale: Strong positive signals for oil & gas industry

✓ Saved 2 trading ideas to data/trading_ideas.json
```

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you created a `.env` file (not `.env.example`)
- Check that the API key is on the correct line
- No quotes needed around the API key

### "google-generativeai library not installed"
```bash
pip install google-generativeai
```

### "Connection failed to trumpstruth.org"
- Check your internet connection
- The site might be temporarily down
- The monitor will keep trying

### spaCy Model Missing
```bash
python -m spacy download en_core_web_sm
```

## Using Without AI (Basic Mode)

If you don't want to use Gemini AI, the system works fine without it:

1. Don't add `GEMINI_API_KEY` to `.env`
2. The system will use basic sentiment analysis
3. You'll still get trading ideas, just without AI enhancement

## File Outputs

All data is saved to `data/` folder:

- **`trading_ideas.json`** - All trading ideas with full details
- **`post_analysis.json`** - Complete analysis of each post
- **`monitor_state.json`** - Tracking state (for restarts)

## View Your Trading Ideas

```bash
# Windows
type data\trading_ideas.json

# Linux/Mac
cat data/trading_ideas.json
```

Or open in any text editor or JSON viewer.

## Next Steps

1. **Let it run** - The monitor checks for new posts every 60 seconds
2. **Review ideas** - Check `data/trading_ideas.json` periodically
3. **Do research** - Use ideas as starting points, not final decisions
4. **Adjust settings** - Change `CHECK_INTERVAL_SECONDS` in `.env`

## Important Reminders

- ⚠️ **Not financial advice** - For educational purposes only
- 📊 **Do your own research** - Always verify before trading
- 💰 **Risk management** - Never risk more than you can afford to lose
- 🎯 **Use as a tool** - One data point among many

## Getting Help

If you encounter issues:

1. Check this QUICKSTART.md
2. Read USAGE.md for detailed info
3. Run test scripts to isolate problems:
   - `python test_gemini.py` - Test AI
   - `python test_system.py` - Test full system

## Gemini API Limits (FREE Tier)

Google's FREE Gemini API includes:
- **60 requests per minute**
- **1,500 requests per day**

For this application (checking every 60 seconds):
- Max: **1,440 requests per day**
- You're well within the free limits!

## Enjoy! 🚀📈

Your Trump Truth Social Trading Monitor is now running and will alert you to potential trading opportunities based on real-time posts.

Stop the monitor anytime with `Ctrl+C`.

