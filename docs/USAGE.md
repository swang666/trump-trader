# Usage Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   # Windows
   install.bat
   
   # Linux/Mac
   chmod +x install.sh
   ./install.sh
   ```

2. **Configure (Optional):**
   - Copy `.env.example` to `.env`
   - Add your Google Gemini API key for enhanced AI analysis (optional but recommended)
   - Get free API key at: https://makersuite.google.com/app/apikey
   - Adjust `CHECK_INTERVAL_SECONDS` if needed

3. **Test Gemini API (optional):**
   ```bash
   python test_gemini.py
   ```

4. **Test the system:**
   ```bash
   python test_system.py
   ```

5. **Start monitoring:**
   ```bash
   python main.py
   ```

## How It Works

### 1. Scraper (`scraper.py`)
- Monitors Trump's Truth Social posts from trumpstruth.org
- Checks for new posts at regular intervals (default: 60 seconds)
- Supports both RSS feed and web scraping
- Tracks the last seen post to avoid duplicates

### 2. Analyzer (`analyzer.py`)
- Performs sentiment analysis on each post
- Extracts mentioned companies and sectors
- Identifies market-relevant topics
- Calculates market relevance score (0-1)
- Optional: Uses Google Gemini AI for advanced analysis

### 3. Trading Ideas Generator (`trading_ideas.py`)
- Generates actionable trading ideas based on analysis
- Provides specific stock tickers or ETFs
- Includes confidence levels and risk assessments
- Suggests timeframes (short/medium/long term)

### 4. Main Monitor (`main.py`)
- Orchestrates all components
- Runs continuously, checking for new posts
- Saves analysis and trading ideas to JSON files
- Maintains state between restarts

## Data Output

All data is saved to the `data/` directory:

- **`trading_ideas.json`** - All generated trading ideas
- **`post_analysis.json`** - Detailed analysis of each post
- **`monitor_state.json`** - Current monitoring state

## Understanding Trading Ideas

Each trading idea includes:

- **Ticker**: Stock symbol or ETF
- **Action**: Buy, Sell, or Short
- **Direction**: Long or Short
- **Confidence**: Low, Medium, or High
- **Timeframe**: Short-term, Medium-term, or Long-term
- **Risk Level**: Low, Medium, High
- **Rationale**: Explanation for the trade

### Confidence Levels

- **High**: Strong signal with clear sentiment and high urgency
- **Medium**: Moderate signal with some supporting factors
- **Low**: Weak signal or conflicting information

### Risk Levels

- **High**: Low confidence trades, volatile situations
- **Medium**: Standard risk for most trades
- **Low**: High confidence with clear directional bias

## Examples

### Example Post
```
"Just announced major trade deal with China! Great for Apple and Tesla. 
American manufacturing is BOOMING!"
```

### Generated Ideas
1. **Buy AAPL** (Apple)
   - Confidence: HIGH
   - Timeframe: Short-term
   - Rationale: Positive mention suggests potential upside from trade deal

2. **Buy TSLA** (Tesla)
   - Confidence: HIGH
   - Timeframe: Short-term
   - Rationale: Positive mention in context of manufacturing boom

3. **Buy XLI** (Industrial Sector ETF)
   - Confidence: MEDIUM
   - Timeframe: Medium-term
   - Rationale: Positive sentiment on manufacturing sector

## Advanced Configuration

### Google Gemini AI Integration

For enhanced analysis, add your Google Gemini API key to `.env`:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

**Getting a FREE API Key:**
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy and paste into your `.env` file

**Benefits of using Gemini AI:**
- More sophisticated sentiment analysis
- Better contextual understanding
- Identifies subtle trading signals
- Provides nuanced trading rationales
- FREE tier with generous limits

### Adjusting Check Interval

In `.env`, modify:
```
CHECK_INTERVAL_SECONDS=30  # Check every 30 seconds
```

Recommended settings:
- **High frequency**: 30-60 seconds (real-time trading)
- **Normal**: 60-120 seconds (balanced)
- **Low frequency**: 300+ seconds (research/analysis)

## Monitoring Output

The monitor displays:

```
[2025-10-13 10:30:45] Checking for new posts...
Found 1 new post(s)!

================================================================================
NEW POST DETECTED at 2025-10-13T10:30:00
================================================================================
Content: Just announced major trade deal...
Link: https://trumpstruth.org/...

📊 Analyzing post...
Sentiment: POSITIVE (polarity: 0.65)
Market Relevance: 0.80
Companies mentioned: ['apple', 'tesla']
Sectors: ['manufacturing', 'trade']

💡 Generating trading ideas...

================================================================================
TRADING IDEAS (3 ideas)
================================================================================

1. Buy AAPL (apple)
   Type: COMPANY | Confidence: HIGH | Risk: MEDIUM
   Timeframe: short-term
   Rationale: Positive mention of apple suggests potential upside...

...
```

## Tips for Using Trading Ideas

1. **Don't Trade Blindly**: Use these as starting points for research
2. **Check Multiple Sources**: Verify claims and context
3. **Consider Market Conditions**: Broader market trends matter
4. **Use Stop Losses**: Always manage risk
5. **Position Sizing**: Don't risk more than you can afford to lose

## Troubleshooting

### Connection Issues
If the scraper can't connect to trumpstruth.org:
- Check your internet connection
- The site might be down temporarily
- Try increasing `CHECK_INTERVAL_SECONDS`

### No Trading Ideas Generated
This can happen when:
- Posts have low market relevance
- No specific companies/sectors mentioned
- Sentiment is too neutral

### spaCy Model Error
If you see "spaCy model not found":
```bash
python -m spacy download en_core_web_sm
```

## Disclaimer

**This tool is for educational and research purposes only.**

- Not financial advice
- Past performance doesn't guarantee future results
- Always do your own research
- Consult with financial advisors
- Be aware of risks in trading

## Support

For issues or questions:
- Check the README.md
- Review code documentation
- Test with `test_system.py`

