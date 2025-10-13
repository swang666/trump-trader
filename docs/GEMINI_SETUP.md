# Google Gemini API Setup Guide

## Why Gemini?

Google's Gemini AI provides **FREE, powerful AI analysis** for your trading monitor:

✅ **FREE tier** with generous limits (60 requests/min)  
✅ **No credit card required** to get started  
✅ **Advanced analysis** of posts for trading signals  
✅ **Better than basic sentiment** - understands context and nuance  
✅ **Easy to set up** - takes 2 minutes  

## Step-by-Step Setup

### 1. Visit Google AI Studio
Go to: **https://makersuite.google.com/app/apikey**

(Alternative URL: https://aistudio.google.com/app/apikey)

### 2. Sign In
- Use any Google account (Gmail, Google Workspace, etc.)
- No credit card required

### 3. Create API Key
Click the **"Create API Key"** button (or "Get API Key")

You'll see something like:
```
AIzaSyD_example_key_1234567890abcdefghij
```

### 4. Copy the Key
Click the copy icon or select and copy the entire key

### 5. Add to Your Project

Create a file named `.env` in your project folder:

**Windows (Command Prompt):**
```cmd
copy .env.example .env
notepad .env
```

**Windows (PowerShell):**
```powershell
copy .env.example .env
notepad .env
```

**Linux/Mac:**
```bash
cp .env.example .env
nano .env
```

### 6. Paste Your Key

Edit the `.env` file to look like this:
```bash
# Google Gemini API Key
GEMINI_API_KEY=AIzaSyD_example_key_1234567890abcdefghij

# Monitoring settings
CHECK_INTERVAL_SECONDS=60
```

**Important:**
- Replace the example key with YOUR actual key
- No quotes needed around the key
- No spaces around the `=` sign

### 7. Test It!

```bash
python test_gemini.py
```

**Success looks like:**
```
================================================================================
TESTING GOOGLE GEMINI API
================================================================================

✓ API Key found: AIzaSyD_e...hijk
✓ google-generativeai library installed

📡 Testing API connection...

✅ SUCCESS! Gemini API is working!

Sample Analysis:
--------------------------------------------------------------------------------
The post displays positive sentiment regarding American manufacturing,
specifically mentioning Tesla and Ford's expansion. This could signal
bullish momentum for automotive stocks, particularly TSLA and F.
Traders might consider long positions with appropriate risk management.
--------------------------------------------------------------------------------

================================================================================
✅ Gemini API is ready to use!

You can now run: python main.py
================================================================================
```

## Troubleshooting

### "GEMINI_API_KEY not found"

**Problem:** The `.env` file doesn't exist or is named wrong

**Solution:**
1. Make sure the file is named `.env` (not `.env.txt` or `.env.example`)
2. On Windows, enable "Show file extensions" to verify
3. File should be in the same folder as `main.py`

### "Invalid API key"

**Problem:** Key copied incorrectly or expired

**Solution:**
1. Check for extra spaces before/after the key
2. Generate a new API key
3. Make sure the full key is copied

### "Module 'google.generativeai' not found"

**Problem:** Python package not installed

**Solution:**
```bash
pip install google-generativeai
# or
pip install -r requirements.txt
```

### Rate Limits

**Free Tier Limits:**
- 60 requests per minute
- 1,500 requests per day

**This monitor uses:**
- 1 request per new post
- ~60-1440 requests per day (depending on post frequency)

**You're well within limits!** The free tier is more than enough.

## Security Best Practices

### ✅ DO:
- Keep your `.env` file private
- Add `.env` to `.gitignore` (already done)
- Never commit API keys to GitHub
- Regenerate keys if accidentally exposed

### ❌ DON'T:
- Share your API key publicly
- Commit `.env` to version control
- Post keys in screenshots or videos
- Use the same key across many projects (optional)

## What Gemini Adds to Your Analysis

### Without Gemini (Basic):
```
Sentiment: POSITIVE (0.75)
Companies: ['tesla', 'ford']
Sectors: ['manufacturing']
```

### With Gemini (Enhanced):
```
Sentiment: POSITIVE (0.75)
Companies: ['tesla', 'ford']
Sectors: ['manufacturing']

🤖 Gemini AI Analysis:
   This post signals strong policy support for domestic auto manufacturing,
   particularly benefiting Tesla (TSLA) and Ford (F). The positive sentiment
   around bringing production to the USA could drive short-term bullish
   momentum. Consider monitoring for entry points, especially if accompanied
   by policy announcements. Risk factors include execution challenges and
   supply chain dependencies.
```

**Much more actionable!**

## Verify It's Working

When you run `python main.py`, you should see:

```
================================================================================
TRUMP TRUTH SOCIAL TRADING MONITOR
================================================================================
Monitoring interval: 60 seconds
Press Ctrl+C to stop

✓ Google Gemini AI enabled    <-- This line confirms it's working!
Testing connection to trumpstruth.org...
```

If you see **"✓ Google Gemini AI enabled"**, you're all set! 🎉

## Alternative: Running Without Gemini

The system works fine without Gemini AI:

1. **Don't create** `.env` file (or leave `GEMINI_API_KEY` empty)
2. You'll still get:
   - Sentiment analysis
   - Company/sector extraction
   - Trading ideas
   - Just without the AI-enhanced context

## Getting Help

If you're stuck:

1. ✅ Re-read this guide
2. ✅ Run `python test_gemini.py` to see specific error
3. ✅ Check that `.env` file exists and has correct format
4. ✅ Verify API key at https://makersuite.google.com/app/apikey

## Ready to Go!

Once your test passes, start the monitor:

```bash
python main.py
```

Or use the quick-start scripts:
```bash
run.bat    # Windows
./run.sh   # Linux/Mac
```

Enjoy your AI-powered trading monitor! 🚀📈🤖

