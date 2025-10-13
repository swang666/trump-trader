# Test Suite

This directory contains all test files for the Trump Truth Social Trading Monitor.

## Test Files

### `test_gemini.py`
Tests Google Gemini API connection and functionality.

**Usage:**
```bash
python tests/test_gemini.py
```

**What it tests:**
- API key configuration
- Gemini API connectivity
- Model availability
- Sample analysis generation

### `test_email.py`
Tests email notification system.

**Usage:**
```bash
python tests/test_email.py
```

**What it tests:**
- Email configuration (SMTP)
- Gmail App Password authentication
- HTML email generation
- Email delivery
- Sends actual test email to recipient

**Prerequisites:**
- SENDER_EMAIL configured in `.env`
- SENDER_PASSWORD (Gmail App Password) configured
- RECIPIENT_EMAIL configured

### `test_ai_analysis.py`
Tests AI-powered post analysis.

**Usage:**
```bash
python tests/test_ai_analysis.py
```

**What it tests:**
- Post analysis with Gemini AI
- Company detection with tickers
- Sector identification
- Sentiment analysis
- Trading idea generation
- AI insights and risk factors

### `test_duplicate_prevention.py`
Tests duplicate post prevention.

**Usage:**
```bash
python tests/test_duplicate_prevention.py
```

**What it tests:**
- First post processing creates analysis
- Duplicate post is skipped
- No redundant data created
- State persistence across restarts
- Multiple posts tracked correctly

### `test_system.py`
Tests full system integration.

**Usage:**
```bash
python tests/test_system.py
```

**What it tests:**
- Post scraping from trumpstruth.org
- Full analysis pipeline
- Trading idea generation
- Data persistence
- End-to-end functionality

## Running All Tests

Run all tests in sequence:

```bash
python run_tests.py
```

Or run individually:

```bash
# Test Gemini API
python tests/test_gemini.py

# Test email
python tests/test_email.py

# Test AI analysis
python tests/test_ai_analysis.py

# Test duplicate prevention
python tests/test_duplicate_prevention.py

# Test full system
python tests/test_system.py
```

## Test Requirements

Before running tests, ensure:

1. **Dependencies installed:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Environment configured (`.env` file):**
   ```
   GEMINI_API_KEY=your_key_here
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   RECIPIENT_EMAIL=alerts@email.com
   ```

3. **Internet connection** (for API calls and scraping)

## Expected Results

### ✓ All Tests Pass
```
[OK] Gemini API: PASSED
[OK] Email Notifications: PASSED
[OK] AI Analysis: PASSED
[OK] Full System: PASSED
```

### Troubleshooting

**Gemini API Test Fails:**
- Check GEMINI_API_KEY in `.env`
- Verify API key at https://makersuite.google.com/app/apikey
- Check internet connection

**Email Test Fails:**
- Verify Gmail App Password (not regular password)
- Check SENDER_EMAIL matches Gmail account
- Ensure "Less secure apps" is NOT enabled (use App Password)
- Check firewall/network allows SMTP (port 587)

**AI Analysis Fails:**
- Same as Gemini API test
- Check model name is correct (`gemini-2.5-flash`)

**System Test Fails:**
- Check internet connection
- Verify trumpstruth.org is accessible
- Ensure all dependencies are installed

## Continuous Testing

For development, you can run tests automatically:

```bash
# Watch for changes and re-run tests (requires watchdog)
pip install watchdog
```

Create `watch_tests.sh`:
```bash
#!/bin/bash
while true; do
    python run_tests.py
    sleep 60
done
```

## Test Coverage

These tests cover:
- ✓ API connectivity
- ✓ Email notifications
- ✓ AI analysis
- ✓ Web scraping
- ✓ Data persistence
- ✓ Error handling
- ✓ Integration flows

## Notes

- Some tests make real API calls (uses your quota)
- Email tests send actual emails
- System tests fetch real data from trumpstruth.org
- All tests should complete in under 2 minutes total

