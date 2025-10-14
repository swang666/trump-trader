"""
Send ARK Invest Trades Email
Fetch real ARK trades and send email notification
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sources.ark_scraper import ARKTradesScraper
from sources.ark_analyzer import ARKTradeAnalyzer
from trading_ideas import TradingIdeasGenerator
from email_notifier import EmailNotifier


def main():
    print("=" * 80)
    print("FETCHING REAL ARK INVEST TRADES")
    print("=" * 80)
    
    # Initialize components
    scraper = ARKTradesScraper()
    analyzer = ARKTradeAnalyzer()
    generator = TradingIdeasGenerator()
    email_notifier = EmailNotifier()
    
    if not email_notifier.enabled:
        print("[ERROR] Email notifications are not configured!")
        print("Please set up EMAIL_* variables in your .env file")
        return
    
    # Fetch latest trades
    print("\n[INFO] Fetching latest ARK trades...")
    trades = scraper.fetch_latest_trades(limit=10)
    
    if not trades:
        print("[ERROR] No trades fetched!")
        return
    
    print(f"[OK] Fetched {len(trades)} trades")
    
    # Analyze and send email for significant trades
    emails_sent = 0
    
    for i, trade in enumerate(trades[:5], 1):  # Process top 5 trades
        print(f"\n[{i}] Analyzing: {trade['title']}")
        
        # Analyze the trade
        analysis = analyzer.analyze_trade(trade)
        
        print(f"    Sentiment: {analysis['sentiment'].upper()}")
        print(f"    Confidence: {analysis['confidence'].upper()}")
        print(f"    Market Relevance: {analysis['market_relevance']:.2f}")
        
        # Generate trading ideas
        ideas = []
        if analysis['market_relevance'] >= 0.2:
            ideas = generator.generate_ideas(analysis)
            if ideas:
                print(f"    Trading Ideas: {len(ideas)}")
        
        # Send email for significant trades
        if analysis['market_relevance'] >= 0.5 or analysis['confidence'] == 'high':
            print(f"    [INFO] Sending email notification...")
            success = email_notifier.send_analysis_report(trade, analysis, ideas)
            if success:
                emails_sent += 1
                print(f"    [OK] Email sent!")
        else:
            print(f"    [SKIP] Not significant enough for email")
    
    # Create summary email with all trades
    print(f"\n[INFO] Creating summary email with all {len(trades)} trades...")
    
    # Build summary
    summary_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
            .trade {{ margin: 20px 0; padding: 15px; border-left: 4px solid #667eea; background: #f8f9fa; }}
            .buy {{ border-left-color: #28a745; }}
            .sell {{ border-left-color: #dc3545; }}
            .ticker {{ font-weight: bold; color: #667eea; }}
            .fund {{ color: #6c757d; font-size: 0.9em; }}
            .date {{ color: #6c757d; font-size: 0.85em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 ARK Invest Daily Trades</h1>
            <p>Latest trades from Cathie Wood's ARK Funds</p>
            <p style="font-size: 0.9em;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div style="padding: 20px;">
            <h2>Latest {len(trades)} Trades</h2>
    """
    
    # Group by fund
    fund_trades = {}
    for trade in trades:
        fund = trade['fund']
        if fund not in fund_trades:
            fund_trades[fund] = []
        fund_trades[fund].append(trade)
    
    # Add trades by fund
    for fund, fund_trade_list in fund_trades.items():
        summary_html += f"<h3>{fund}</h3>"
        for trade in fund_trade_list:
            direction_class = 'buy' if trade['direction'] == 'buy' else 'sell'
            direction_emoji = '🟢' if trade['direction'] == 'buy' else '🔴'
            
            summary_html += f"""
            <div class="trade {direction_class}">
                <div class="date">{trade['date']}</div>
                <div>
                    {direction_emoji} <strong>{trade['direction'].upper()}</strong>: 
                    <span class="ticker">{trade['ticker']}</span> - {trade['company']}
                </div>
                <div>Shares: {trade['shares']:,} ({trade['etf_percent']:.2f}% of fund)</div>
            </div>
            """
    
    summary_html += """
        </div>
        <div style="padding: 20px; background: #f8f9fa; margin-top: 20px; text-align: center; color: #6c757d; font-size: 0.9em;">
            <p>Data from ARK Funds API | For informational purposes only</p>
        </div>
    </body>
    </html>
    """
    
    # Send summary email
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import smtplib
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📊 ARK Invest Daily Trades - {len(trades)} Recent Trades"
        msg['From'] = email_notifier.sender_email
        msg['To'] = email_notifier.recipient_email
        
        # Plain text version
        text_content = f"""
ARK INVEST DAILY TRADES
======================

Latest {len(trades)} trades from Cathie Wood's ARK Funds
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        for trade in trades:
            direction_arrow = '↑' if trade['direction'] == 'buy' else '↓'
            text_content += f"""
{trade['date']} | {trade['fund']}
{direction_arrow} {trade['direction'].upper()}: {trade['ticker']} - {trade['company']}
Shares: {trade['shares']:,} ({trade['etf_percent']:.2f}% of fund)

"""
        
        text_content += "\nData from ARK Funds API | For informational purposes only"
        
        # Attach both versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(summary_html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send
        with smtplib.SMTP(email_notifier.smtp_server, email_notifier.smtp_port) as server:
            server.starttls()
            server.login(email_notifier.sender_email, email_notifier.sender_password)
            server.send_message(msg)
        
        print(f"[OK] Summary email sent to {email_notifier.recipient_email}")
        print(f"\n{'=' * 80}")
        print(f"[SUCCESS] Sent {emails_sent + 1} email(s) total")
        print(f"{'=' * 80}")
        
    except Exception as e:
        print(f"[ERROR] Failed to send summary email: {e}")


if __name__ == "__main__":
    main()

