"""
Test Email Notification System
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_notifier import EmailNotifier
from datetime import datetime


def main():
    print("="*80)
    print("TESTING EMAIL NOTIFICATION SYSTEM")
    print("="*80)
    print()
    
    notifier = EmailNotifier()
    
    if not notifier.enabled:
        print("[ERROR] Email notifications are NOT configured!")
        print()
        print("To enable email notifications, add these to your .env file:")
        print()
        print("SENDER_EMAIL=your_email@gmail.com")
        print("SENDER_PASSWORD=your_gmail_app_password")
        print("RECIPIENT_EMAIL=recipient@email.com")
        print()
        print("For Gmail App Password, visit:")
        print("https://myaccount.google.com/apppasswords")
        print()
        print("Steps:")
        print("1. Go to link above")
        print("2. Select 'Mail' and 'Other (custom name)'")
        print("3. Name it 'Trump Trader Monitor'")
        print("4. Copy the 16-character password")
        print("5. Add to .env as SENDER_PASSWORD")
        return
    
    print(f"[OK] Email notifications configured")
    print(f"     From: {notifier.sender_email}")
    print(f"     To: {notifier.recipient_email}")
    print(f"     SMTP: {notifier.smtp_server}:{notifier.smtp_port}")
    print()
    
    # Create test data
    test_post = {
        'id': 'test_email_123',
        'content': '''BREAKING: Just had a fantastic meeting with Tim Cook and Elon Musk! 
        
Apple is bringing iPhone manufacturing back to America - HUGE for jobs!
Tesla's new Gigafactory in Texas is already producing. American manufacturing is BOOMING!

This is what WINNING looks like! #MAGA #AmericaFirst''',
        'link': 'https://trumpstruth.org/test/123',
        'timestamp': datetime.now().isoformat()
    }
    
    test_analysis = {
        'post_id': 'test_email_123',
        'timestamp': datetime.now().isoformat(),
        'content_preview': test_post['content'][:200],
        'sentiment': {
            'label': 'positive',
            'polarity': 0.85,
            'confidence': 0.9
        },
        'companies': [
            {
                'name': 'Apple',
                'ticker': 'AAPL',
                'sentiment': 'positive',
                'reason': 'Bringing iPhone manufacturing back to America indicates significant domestic investment and job creation'
            },
            {
                'name': 'Tesla',
                'ticker': 'TSLA',
                'sentiment': 'positive',
                'reason': 'New Gigafactory in Texas already producing, showing expansion and growth'
            }
        ],
        'sectors': ['Technology', 'Manufacturing', 'Automotive'],
        'topics': ['Manufacturing', 'Jobs', 'American Economy', 'Domestic Investment'],
        'urgency': 'high',
        'market_relevance': 0.90,
        'ai_insights': '''This post signals strong policy support for domestic manufacturing, particularly benefiting Apple (AAPL) and Tesla (TSLA). The positive sentiment around reshoring production could drive short-term bullish momentum for both stocks. Investors may anticipate increased domestic investment and job creation, which could attract positive market attention. The emphasis on "American manufacturing booming" suggests broader sector strength.''',
        'risk_factors': '''The primary risk is verification of these claims. Major manufacturing shifts require extensive planning and official company announcements. Investor sentiment could be volatile if claims are not substantiated by Apple or Tesla directly. Additionally, geopolitical factors and supply chain complexities may challenge large-scale reshoring efforts. Market reaction could be short-lived without concrete follow-through.''',
        'analysis_method': 'ai'
    }
    
    test_trading_ideas = [
        {
            'ticker': 'AAPL',
            'name': 'Apple',
            'action': 'Buy',
            'direction': 'long',
            'type': 'company',
            'confidence': 'high',
            'risk_level': 'medium',
            'timeframe': 'short-term',
            'urgency': 'high',
            'rationale': 'Positive mention of bringing iPhone manufacturing to USA suggests potential upside. Domestic production narrative could drive investor interest and stock appreciation in the near term.'
        },
        {
            'ticker': 'TSLA',
            'name': 'Tesla',
            'action': 'Buy',
            'direction': 'long',
            'type': 'company',
            'confidence': 'high',
            'risk_level': 'medium',
            'timeframe': 'short-term',
            'urgency': 'high',
            'rationale': 'New Texas Gigafactory already producing indicates successful expansion. Positive political support could benefit stock sentiment and attract momentum traders.'
        },
        {
            'ticker': 'XLI',
            'name': 'Industrial Sector ETF',
            'action': 'Buy',
            'direction': 'long',
            'type': 'sector',
            'confidence': 'medium',
            'risk_level': 'medium',
            'timeframe': 'medium-term',
            'urgency': 'medium',
            'rationale': 'Positive sentiment on American manufacturing sector suggests potential strength in industrial stocks. Manufacturing boom narrative could drive sector-wide gains.'
        }
    ]
    
    print("Sending test email with sample analysis...")
    print()
    
    success = notifier.send_analysis_report(test_post, test_analysis, test_trading_ideas)
    
    print()
    print("="*80)
    if success:
        print("[SUCCESS] Test email sent!")
        print()
        print("Check your inbox at:", notifier.recipient_email)
        print()
        print("The email includes:")
        print("  - Post content")
        print("  - Sentiment analysis")
        print("  - Companies mentioned (AAPL, TSLA)")
        print("  - AI insights")
        print("  - Risk factors")
        print("  - 3 trading ideas")
        print()
        print("Both plain text and HTML versions were sent.")
    else:
        print("[FAILED] Could not send test email")
        print()
        print("Possible issues:")
        print("  - Incorrect Gmail App Password")
        print("  - SENDER_EMAIL doesn't match Gmail account")
        print("  - Network/firewall blocking SMTP")
        print("  - SMTP server/port incorrect")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

