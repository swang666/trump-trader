"""
Test ARK trade email with real analysis
"""
from sources.ark_analyzer import ARKTradeAnalyzer
from email_notifier import EmailNotifier
from datetime import datetime

# Create a test ARK trade
test_trade = {
    'id': 'ark_test_email_2025',
    'source': 'ARK_INVEST',
    'timestamp': datetime.now().isoformat(),
    'date': '2025-10-14',
    'fund': 'ARKK',
    'ticker': 'TSLA',
    'company': 'Tesla Inc',
    'direction': 'buy',
    'shares': 500000,
    'etf_percent': 1.25,
    'content': 'Cathie Wood\'s ARKK bought 500K shares of TSLA (Tesla Inc), representing 1.25% of the fund',
    'type': 'trade',
    'link': 'https://arkfunds.io/trades/arkk',
    'trader': 'Cathie Wood (ARK Invest)'
}

print("Testing ARK email notification...")
print(f"Trade: {test_trade['content']}\n")

# Analyze
analyzer = ARKTradeAnalyzer()
analysis = analyzer.analyze_trade(test_trade)

print(f"Analysis:")
print(f"  Sentiment: {analysis['sentiment']}")
print(f"  Confidence: {analysis['confidence']}")
print(f"  Market Relevance: {analysis['market_relevance']}")

# Send email
notifier = EmailNotifier()
if notifier.enabled:
    print("\nSending test email...")
    success = notifier.send_analysis_report(test_trade, analysis, [])
    if success:
        print("[OK] Email sent successfully!")
    else:
        print("[ERROR] Email failed!")
else:
    print("[ERROR] Email notifications not enabled!")

