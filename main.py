"""
Multi-Source Trading Monitor
Monitors Trump Truth Social + ARK Invest Trades + More
"""

import time
import json
import os
import logging
import subprocess
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

# Import scrapers
from sources.truth_social_scraper import TruthSocialScraper
from sources.ark_scraper import ARKTradesScraper
from sources.ark_analyzer import ARKTradeAnalyzer

# Import analyzers and generators
from analyzer import PostAnalyzer
from trading_ideas import TradingIdeasGenerator
from email_notifier import EmailNotifier

load_dotenv()

# Configure logging for production (minimal console output for GCE)
file_handler = logging.FileHandler('trading_monitor.log')
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
        subprocess.run(['clear'], check=False, capture_output=True)
    except:
        print('\n' * 50)


class MultiSourceTradingMonitor:
    """Main application class - monitors multiple market-moving sources"""
    
    def __init__(self, check_interval: int = 60):
        # Initialize scrapers
        self.truth_scraper = TruthSocialScraper()
        self.ark_scraper = ARKTradesScraper()
        
        # Initialize analyzers
        self.post_analyzer = PostAnalyzer(use_ai=True)
        self.ark_analyzer = ARKTradeAnalyzer()
        
        # Initialize generators and notifiers
        self.generator = TradingIdeasGenerator()
        self.email_notifier = EmailNotifier()
        
        self.check_interval = check_interval
        self.running = False
        self.processed_items = set()  # Track processed item IDs (posts + trades)
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load state
        self.state_file = 'data/monitor_state.json'
        self.load_state()
    
    def load_state(self):
        """Load monitor state"""
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.truth_scraper.last_post_id = state.get('last_truth_post_id')
                self.processed_items = set(state.get('processed_items', []))
                logger.info(f"Loaded state: {len(self.processed_items)} items processed")
                logger.info(f"Last Truth Social post: {self.truth_scraper.last_post_id}")
        except FileNotFoundError:
            logger.info("No previous state found, starting fresh")
    
    def save_state(self):
        """Save monitor state"""
        try:
            state = {
                'last_truth_post_id': self.truth_scraper.last_post_id,
                'processed_items': list(self.processed_items),
                'last_check': datetime.now().isoformat(),
                'total_processed': len(self.processed_items)
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def process_item(self, item: Dict):
        """Process a single item (post or trade)"""
        item_id = item.get('id')
        item_source = item.get('source', 'UNKNOWN')
        item_type = item.get('type', 'post')
        
        # Skip if already processed
        if item_id in self.processed_items:
            logger.debug(f"SKIP: {item_source} item {item_id} already processed")
            return
        
        logger.info(f"NEW {item_type.upper()} DETECTED from {item_source} at {item['timestamp']}")
        
        # Get content
        content = item.get('content', '').strip()
        
        # Check if content is empty or too short
        if not content or len(content) < 2:
            logger.debug(f"SKIP: Content is empty or too short (length: {len(content)})")
            # Still mark as processed to avoid checking again
            self.processed_items.add(item_id)
            self.save_state()
            return
        
        logger.debug(f"Content: {content[:200]}...")
        logger.debug(f"Link: {item.get('link', 'N/A')}")
        
        # Choose appropriate analyzer based on source
        logger.info("Analyzing item...")
        if item_source == 'ARK_INVEST':
            analysis = self.ark_analyzer.analyze_trade(item)
        else:
            analysis = self.post_analyzer.analyze_post(item)
        
        # Log analysis results
        if 'sentiment' in analysis:
            if isinstance(analysis['sentiment'], dict):
                logger.debug(f"Sentiment: {analysis['sentiment']['label'].upper()} "
                           f"(polarity: {analysis['sentiment']['polarity']:.2f})")
            else:
                logger.debug(f"Sentiment: {analysis.get('sentiment', 'NEUTRAL').upper()}")
        
        logger.debug(f"Market Relevance: {analysis['market_relevance']:.2f}")
        
        if analysis['companies']:
            companies_str = ', '.join([f"{c.get('name', '')} ({c.get('ticker', 'N/A')})" for c in analysis['companies']])
            logger.debug(f"Companies: {companies_str}")
        if analysis['sectors']:
            logger.debug(f"Sectors: {', '.join(analysis['sectors'])}")
        if analysis['topics']:
            logger.debug(f"Topics: {', '.join(analysis['topics'])}")
        
        # Log AI insights
        if analysis.get('ai_insights'):
            logger.debug(f"AI INSIGHTS: {analysis['ai_insights']}")
        
        if analysis.get('risk_factors'):
            logger.debug(f"RISK FACTORS: {analysis['risk_factors']}")
        
        # Generate trading ideas
        if analysis['market_relevance'] >= 0.2:
            logger.info("Generating trading ideas...")
            ideas = self.generator.generate_ideas(analysis)
            
            if ideas:
                logger.debug(self.generator.format_ideas_for_display(ideas))
                
                # Save ideas
                self.generator.save_ideas(ideas)
                logger.info(f"Saved {len(ideas)} trading ideas to data/trading_ideas.json")
            else:
                logger.info("No specific trading ideas generated from this post.")
                ideas = []
        else:
            logger.info("Low market relevance - skipping trading idea generation")
            ideas = []
        
        # Save analysis
        self.save_analysis(analysis)
        
        # Send email notifications only for non-ARK sources
        # ARK trades are sent via daily digest (send_ark_email.py)
        if item_source != 'ARK_INVEST':
            # Determine if this post is significant enough to send email
            should_send_email = self._should_send_email_notification(analysis, ideas)
            
            # Send email notification only if significant
            if not self.email_notifier.enabled:
                logger.info("Email notifications are disabled")
            elif should_send_email:
                logger.info("Sending email notification...")
                self.email_notifier.send_analysis_report(item, analysis, ideas)
            else:
                logger.info("Item not significant enough for email notification")
                logger.info(f"Market relevance: {analysis['market_relevance']:.2f} (threshold: 0.3)")
                logger.info(f"Companies found: {len(analysis['companies'])}")
                logger.info(f"Trading ideas: {len(ideas)}")
        else:
            logger.info("ARK trade - skipping individual email (sent via daily digest)")
        
        # Mark as processed
        self.processed_items.add(item_id)
        logger.info(f"{item_source} item {item_id} processed and marked")
        self.save_state()
        
        # Clear console periodically to prevent buffer buildup
        clear_console_safely()
    
    def _should_send_email_notification(self, analysis: Dict, trading_ideas: list) -> bool:
        """
        Determine if the post is significant enough to send email notification
        
        Args:
            analysis: Analysis results
            trading_ideas: List of generated trading ideas
            
        Returns:
            True if email should be sent, False otherwise
        """
        # Check 1: Market relevance score must be meaningful
        market_relevance = analysis.get('market_relevance', 0.0)
        if market_relevance < 0.3:
            return False
        
        # Check 2: Must have at least one of these:
        # - Companies mentioned
        # - Trading ideas generated
        # - High urgency
        has_companies = len(analysis.get('companies', [])) > 0
        has_trading_ideas = len(trading_ideas) > 0
        high_urgency = analysis.get('urgency', 'low') in ['high', 'medium']
        
        if not (has_companies or has_trading_ideas or high_urgency):
            return False
        
        # Check 3: Content must be substantial (for email)
        content_preview = analysis.get('content_preview', '')
        if len(content_preview.strip()) < 2:
            return False
        
        # All checks passed
        return True
    
    def save_analysis(self, analysis: Dict):
        """Save analysis to file"""
        filepath = 'data/post_analysis.json'
        try:
            # Load existing analyses
            try:
                with open(filepath, 'r') as f:
                    existing = json.load(f)
            except FileNotFoundError:
                existing = []
            
            # Append new analysis
            existing.append(analysis)
            
            # Save back
            with open(filepath, 'w') as f:
                json.dump(existing, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
    
    def check_all_sources(self):
        """Check all sources for new items"""
        all_items = []
        
        # Check Truth Social
        try:
            truth_posts = self.truth_scraper.get_new_posts()
            all_items.extend(truth_posts)
            if truth_posts:
                logger.info(f"Found {len(truth_posts)} new Truth Social post(s)")
        except Exception as e:
            logger.error(f"Truth Social check failed: {e}")
        
        # Check ARK Trades
        try:
            ark_trades = self.ark_scraper.fetch_latest_trades(limit=20)
            # Filter out already processed trades
            new_ark_trades = [t for t in ark_trades if t['id'] not in self.processed_items]
            all_items.extend(new_ark_trades)
            if new_ark_trades:
                logger.info(f"Found {len(new_ark_trades)} new ARK trade(s)")
        except Exception as e:
            logger.error(f"ARK trades check failed: {e}")
        
        return all_items
    
    def run_once(self):
        """Run one check cycle"""
        logger.info(f"Checking all sources at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            new_items = self.check_all_sources()
            
            if new_items:
                logger.info(f"Found {len(new_items)} new item(s) total!")
                
                # Separate ARK trades from other items
                ark_trades = [item for item in new_items if item.get('source') == 'ARK_INVEST']
                other_items = [item for item in new_items if item.get('source') != 'ARK_INVEST']
                
                # Process non-ARK items normally
                for item in other_items:
                    self.process_item(item)
                
                # Process ARK trades (they will be analyzed and marked, but not emailed individually)
                for item in ark_trades:
                    self.process_item(item)
                
                # Send consolidated ARK digest email if there are new trades
                if ark_trades and self.email_notifier.enabled:
                    logger.info(f"Sending consolidated ARK digest for {len(ark_trades)} trade(s)")
                    self.send_ark_digest(ark_trades)
            else:
                logger.debug("No new items found from any source.")
        
        except Exception as e:
            logger.error(f"Error during check: {e}")
            import traceback
            traceback.print_exc()
    
    def send_ark_digest(self, trades):
        """Send consolidated ARK trades digest email"""
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import smtplib
        
        try:
            # Build HTML digest
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
                    .date {{ color: #6c757d; font-size: 0.85em; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 ARK Invest New Trades Detected</h1>
                    <p>Latest trades from Cathie Wood's ARK Funds</p>
                    <p style="font-size: 0.9em;">Detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div style="padding: 20px;">
                    <h2>{len(trades)} New Trade(s)</h2>
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
            
            # Build plain text version
            text_content = f"""
ARK INVEST NEW TRADES
=====================

{len(trades)} new trade(s) detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
            for trade in trades:
                direction_arrow = '↑' if trade['direction'] == 'buy' else '↓'
                text_content += f"""
{trade['date']} | {trade['fund']}
{direction_arrow} {trade['direction'].upper()}: {trade['ticker']} - {trade['company']}
Shares: {trade['shares']:,} ({trade['etf_percent']:.2f}% of fund)

"""
            
            # Create and send email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"📊 ARK Invest: {len(trades)} New Trade(s) Detected"
            msg['From'] = self.email_notifier.sender_email
            msg['To'] = self.email_notifier.recipient_email
            
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(summary_html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send
            with smtplib.SMTP(self.email_notifier.smtp_server, self.email_notifier.smtp_port) as server:
                server.starttls()
                server.login(self.email_notifier.sender_email, self.email_notifier.sender_password)
                server.send_message(msg)
            
            logger.info(f"ARK digest email sent successfully to {self.email_notifier.recipient_email}")
            
        except Exception as e:
            logger.error(f"Failed to send ARK digest email: {e}")
    
    def run(self):
        """Run the monitor continuously"""
        logger.info("MULTI-SOURCE TRADING MONITOR")
        logger.info("Sources: Trump Truth Social + ARK Invest Trades")
        logger.info(f"Monitoring interval: {self.check_interval} seconds")
        logger.info(f"Email notifications: {'ENABLED' if self.email_notifier.enabled else 'DISABLED'}")
        
        # Clear console at start
        clear_console_safely()
        
        # Test connection
        logger.info("Testing connection to trumpstruth.org...")
        if self.truth_scraper.test_connection():
            logger.info("Truth Social connection successful")
        else:
            logger.warning("Could not connect to trumpstruth.org - will continue trying")
        
        self.running = True
        
        # Initial check
        self.run_once()
        
        # Continuous monitoring
        try:
            while self.running:
                time.sleep(self.check_interval)
                self.run_once()
        
        except KeyboardInterrupt:
            logger.info("Stopping monitor...")
            self.save_state()
            logger.info("State saved. Goodbye!")
            clear_console_safely()
    
    def stop(self):
        """Stop the monitor"""
        self.running = False


def main():
    # Get check interval from env or use default
    check_interval = int(os.getenv('CHECK_INTERVAL_SECONDS', 60))
    
    # Create and run monitor
    monitor = MultiSourceTradingMonitor(check_interval=check_interval)
    monitor.run()


if __name__ == "__main__":
    main()

