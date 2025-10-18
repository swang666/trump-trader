"""
Send ARK Invest Trades Email
Fetch real ARK trades and send email notification
"""

import sys
import os
import logging
import subprocess
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sources.ark_scraper import ARKTradesScraper
from sources.ark_analyzer import ARKTradeAnalyzer
from trading_ideas import TradingIdeasGenerator
from email_notifier import EmailNotifier

# Configure logging for production (minimal console output for GCE)
file_handler = logging.FileHandler('ark_trades.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # Only warnings/errors to console
console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def clear_console_safely():
    """Safely clear console to prevent GCE terminal buffer issues"""
    try:
        # Use system clear command (works on Linux/GCE)
        subprocess.run(['clear'], check=False, capture_output=True)
    except:
        # Fallback: print newlines to push content up
        print('\n' * 50)


def main():
    logger.info("Starting ARK Invest trades email process")
    
    # Clear console at start to ensure clean output
    clear_console_safely()
    
    # Initialize components
    scraper = ARKTradesScraper()
    analyzer = ARKTradeAnalyzer()
    generator = TradingIdeasGenerator()
    email_notifier = EmailNotifier()
    
    if not email_notifier.enabled:
        logger.error("Email notifications are not configured!")
        logger.error("Please set up EMAIL_* variables in your .env file")
        return
    
    # Fetch latest trades
    logger.info("Fetching latest ARK trades...")
    trades = scraper.fetch_latest_trades(limit=10)
    
    if not trades:
        logger.error("No trades fetched!")
        return
    
    logger.info(f"Fetched {len(trades)} trades")
    
    # Clear console after fetching to prevent buffer buildup
    clear_console_safely()
    
    # Analyze trades for summary
    logger.info(f"Analyzing {len(trades)} trades for summary...")
    
    significant_trades = []
    for i, trade in enumerate(trades, 1):
        logger.debug(f"Analyzing trade {i}: {trade['title']}")
        
        # Analyze the trade
        analysis = analyzer.analyze_trade(trade)
        
        logger.debug(f"Trade {i} - Sentiment: {analysis['sentiment'].upper()}, "
                    f"Confidence: {analysis['confidence'].upper()}, "
                    f"Relevance: {analysis['market_relevance']:.2f}")
        
        # Generate trading ideas for significant trades
        ideas = []
        if analysis['market_relevance'] >= 0.2:
            ideas = generator.generate_ideas(analysis)
            if ideas:
                logger.debug(f"Trade {i} - Generated {len(ideas)} trading ideas")
        
        # Track significant trades for summary
        if analysis['market_relevance'] >= 0.3 or analysis['confidence'] == 'high':
            significant_trades.append({
                'trade': trade,
                'analysis': analysis,
                'ideas': ideas
            })
            logger.debug(f"Trade {i} - Added to summary (significant)")
        else:
            logger.debug(f"Trade {i} - Not significant enough for summary")
        
        # Clear console every 5 trades to prevent buffer buildup
        if i % 5 == 0:
            clear_console_safely()
    
    # Create consolidated summary email
    logger.info(f"Creating consolidated summary email...")
    logger.info(f"Total trades: {len(trades)}, Significant trades: {len(significant_trades)}")
    
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
            .analysis {{ margin-top: 10px; padding: 10px; background: #e9ecef; border-radius: 5px; }}
            .sentiment {{ font-weight: bold; }}
            .positive {{ color: #28a745; }}
            .negative {{ color: #dc3545; }}
            .neutral {{ color: #6c757d; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 ARK Invest Daily Trades</h1>
            <p>Latest trades from Cathie Wood's ARK Funds</p>
            <p style="font-size: 0.9em;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div style="padding: 20px;">
            <h2>All {len(trades)} Recent Trades</h2>
    """
    
    # Group by fund
    fund_trades = {}
    for trade in trades:
        fund = trade['fund']
        if fund not in fund_trades:
            fund_trades[fund] = []
        fund_trades[fund].append(trade)
    
    # Add trades by fund with analysis for significant ones
    for fund, fund_trade_list in fund_trades.items():
        summary_html += f"<h3>{fund}</h3>"
        for trade in fund_trade_list:
            direction_class = 'buy' if trade['direction'] == 'buy' else 'sell'
            direction_emoji = '🟢' if trade['direction'] == 'buy' else '🔴'
            
            # Check if this trade has analysis
            trade_analysis = None
            for sig_trade in significant_trades:
                if sig_trade['trade']['ticker'] == trade['ticker'] and sig_trade['trade']['date'] == trade['date']:
                    trade_analysis = sig_trade
                    break
            
            summary_html += f"""
            <div class="trade {direction_class}">
                <div class="date">{trade['date']}</div>
                <div>
                    {direction_emoji} <strong>{trade['direction'].upper()}</strong>: 
                    <span class="ticker">{trade['ticker']}</span> - {trade['company']}
                </div>
                <div>Shares: {trade['shares']:,} ({trade['etf_percent']:.2f}% of fund)</div>
            """
            
            # Add analysis if available
            if trade_analysis:
                analysis = trade_analysis['analysis']
                sentiment_class = 'positive' if analysis['sentiment'] == 'positive' else 'negative' if analysis['sentiment'] == 'negative' else 'neutral'
                
                summary_html += f"""
                <div class="analysis">
                    <div><span class="sentiment {sentiment_class}">Sentiment: {analysis['sentiment'].upper()}</span> | 
                         Confidence: {analysis['confidence'].upper()} | 
                         Relevance: {analysis['market_relevance']:.2f}</div>
                """
                
                # Add trading ideas if available
                if trade_analysis['ideas']:
                    summary_html += "<div><strong>Trading Ideas:</strong><ul>"
                    for idea in trade_analysis['ideas'][:3]:  # Show top 3 ideas
                        summary_html += f"<li>{idea.get('idea', 'N/A')} (Confidence: {idea.get('confidence', 'N/A')})</li>"
                    summary_html += "</ul></div>"
                
                summary_html += "</div>"
            
            summary_html += "</div>"
    
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
        
        logger.info(f"Consolidated summary email sent to {email_notifier.recipient_email}")
        logger.info(f"SUCCESS: Sent 1 consolidated email with {len(trades)} trades "
                   f"({len(significant_trades)} significant trades with analysis)")
        
        # Final console clear for clean completion
        clear_console_safely()
        
    except Exception as e:
        logger.error(f"Failed to send summary email: {e}")
        clear_console_safely()


if __name__ == "__main__":
    main()

