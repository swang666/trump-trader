"""
Multi-Source Trading Monitor
Monitors Trump Truth Social + ARK Invest Trades + More
"""

import time
import json
import os
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
                print(f"[OK] Loaded state: {len(self.processed_items)} items processed")
                print(f"     Last Truth Social post: {self.truth_scraper.last_post_id}")
        except FileNotFoundError:
            print("[INFO] No previous state found, starting fresh")
    
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
            print(f"[ERROR] Failed to save state: {e}")
    
    def process_item(self, item: Dict):
        """Process a single item (post or trade)"""
        item_id = item.get('id')
        item_source = item.get('source', 'UNKNOWN')
        item_type = item.get('type', 'post')
        
        # Skip if already processed
        if item_id in self.processed_items:
            print(f"[SKIP] {item_source} item {item_id} already processed")
            return
        
        print(f"\n{'='*80}")
        print(f"NEW {item_type.upper()} DETECTED from {item_source} at {item['timestamp']}")
        print(f"{'='*80}")
        
        # Get content
        content = item.get('content', '').strip()
        
        # Check if content is empty or too short
        if not content or len(content) < 2:
            print(f"[SKIP] Content is empty or too short (length: {len(content)})")
            print("[INFO] Not processing empty item")
            # Still mark as processed to avoid checking again
            self.processed_items.add(item_id)
            self.save_state()
            return
        
        print(f"Content: {content[:200]}...")
        print(f"Link: {item.get('link', 'N/A')}")
        
        # Choose appropriate analyzer based on source
        print("\n[INFO] Analyzing item...")
        if item_source == 'ARK_INVEST':
            analysis = self.ark_analyzer.analyze_trade(item)
        else:
            analysis = self.post_analyzer.analyze_post(item)
        
        # Display sentiment
        if 'sentiment' in analysis:
            if isinstance(analysis['sentiment'], dict):
                print(f"Sentiment: {analysis['sentiment']['label'].upper()} "
                      f"(polarity: {analysis['sentiment']['polarity']:.2f})")
            else:
                print(f"Sentiment: {analysis.get('sentiment', 'NEUTRAL').upper()}")
        
        print(f"Market Relevance: {analysis['market_relevance']:.2f}")
        
        if analysis['companies']:
            companies_str = ', '.join([f"{c.get('name', '')} ({c.get('ticker', 'N/A')})" for c in analysis['companies']])
            print(f"Companies: {companies_str}")
        if analysis['sectors']:
            print(f"Sectors: {', '.join(analysis['sectors'])}")
        if analysis['topics']:
            print(f"Topics: {', '.join(analysis['topics'])}")
        
        # Display AI insights
        if analysis.get('ai_insights'):
            print(f"\n[AI INSIGHTS]")
            print(f"   {analysis['ai_insights']}")
        
        if analysis.get('risk_factors'):
            print(f"\n[RISK FACTORS]")
            print(f"   {analysis['risk_factors']}")
        
        # Generate trading ideas
        if analysis['market_relevance'] >= 0.2:
            print("\n[INFO] Generating trading ideas...")
            ideas = self.generator.generate_ideas(analysis)
            
            if ideas:
                print(self.generator.format_ideas_for_display(ideas))
                
                # Save ideas
                self.generator.save_ideas(ideas)
                print(f"[OK] Saved {len(ideas)} trading ideas to data/trading_ideas.json")
            else:
                print("[INFO] No specific trading ideas generated from this post.")
                ideas = []
        else:
            print("\n[INFO] Low market relevance - skipping trading idea generation")
            ideas = []
        
        # Save analysis
        self.save_analysis(analysis)
        
        # Determine if this post is significant enough to send email
        should_send_email = self._should_send_email_notification(analysis, ideas)
        
        # Send email notification only if significant
        if self.email_notifier.enabled and should_send_email:
            print("\n[INFO] Sending email notification...")
            self.email_notifier.send_analysis_report(item, analysis, ideas)
        elif self.email_notifier.enabled and not should_send_email:
            print("\n[SKIP] Item not significant enough for email notification")
            print(f"       Market relevance: {analysis['market_relevance']:.2f}")
            print(f"       Companies found: {len(analysis['companies'])}")
            print(f"       Trading ideas: {len(ideas)}")
        
        # Mark as processed
        self.processed_items.add(item_id)
        print(f"[OK] {item_source} item {item_id} processed and marked")
        self.save_state()
    
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
            print(f"Error saving analysis: {e}")
    
    def check_all_sources(self):
        """Check all sources for new items"""
        all_items = []
        
        # Check Truth Social
        try:
            truth_posts = self.scraper.get_new_posts()
            all_items.extend(truth_posts)
            if truth_posts:
                print(f"[OK] Found {len(truth_posts)} new Truth Social post(s)")
        except Exception as e:
            print(f"[ERROR] Truth Social check failed: {e}")
        
        # Check ARK Trades
        try:
            ark_trades = self.ark_scraper.fetch_latest_trades(limit=20)
            # Filter out already processed trades
            new_ark_trades = [t for t in ark_trades if t['id'] not in self.processed_items]
            all_items.extend(new_ark_trades)
            if new_ark_trades:
                print(f"[OK] Found {len(new_ark_trades)} new ARK trade(s)")
        except Exception as e:
            print(f"[ERROR] ARK trades check failed: {e}")
        
        return all_items
    
    def run_once(self):
        """Run one check cycle"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking all sources...")
        
        try:
            new_items = self.check_all_sources()
            
            if new_items:
                print(f"Found {len(new_items)} new item(s) total!")
                for item in new_items:
                    self.process_item(item)
            else:
                print("No new items found from any source.")
        
        except Exception as e:
            print(f"Error during check: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run the monitor continuously"""
        print("="*80)
        print("MULTI-SOURCE TRADING MONITOR")
        print("="*80)
        print("Sources: Trump Truth Social + ARK Invest Trades")
        print(f"Monitoring interval: {self.check_interval} seconds")
        print(f"Email notifications: {'ENABLED' if self.email_notifier.enabled else 'DISABLED'}")
        print("Press Ctrl+C to stop\n")
        
        # Test connection
        print("Testing connection to trumpstruth.org...")
        if self.scraper.test_connection():
            print("[OK] Truth Social connection successful\n")
        else:
            print("[WARNING] Could not connect to trumpstruth.org")
            print("Will continue trying...\n")
        
        self.running = True
        
        # Initial check
        self.run_once()
        
        # Continuous monitoring
        try:
            while self.running:
                time.sleep(self.check_interval)
                self.run_once()
        
        except KeyboardInterrupt:
            print("\n\n[INFO] Stopping monitor...")
            self.save_state()
            print("State saved. Goodbye!")
    
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

