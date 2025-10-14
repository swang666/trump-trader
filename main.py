"""
Trump Truth Social Trading Monitor
Main application entry point
"""

import time
import json
import os
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

from scraper import TruthSocialScraper
from analyzer import PostAnalyzer
from trading_ideas import TradingIdeasGenerator
from email_notifier import EmailNotifier

load_dotenv()


class TruthTradingMonitor:
    """Main application class"""
    
    def __init__(self, check_interval: int = 60):
        self.scraper = TruthSocialScraper()
        self.analyzer = PostAnalyzer(use_ai=True)
        self.generator = TradingIdeasGenerator()
        self.email_notifier = EmailNotifier()
        self.check_interval = check_interval
        self.running = False
        self.processed_posts = set()  # Track processed post IDs
        
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
                self.scraper.last_post_id = state.get('last_post_id')
                self.processed_posts = set(state.get('processed_posts', []))
                print(f"[OK] Loaded state: {len(self.processed_posts)} posts processed")
                print(f"     Last post ID: {self.scraper.last_post_id}")
        except FileNotFoundError:
            print("[INFO] No previous state found, starting fresh")
    
    def save_state(self):
        """Save monitor state"""
        try:
            state = {
                'last_post_id': self.scraper.last_post_id,
                'processed_posts': list(self.processed_posts),
                'last_check': datetime.now().isoformat(),
                'total_processed': len(self.processed_posts)
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save state: {e}")
    
    def process_post(self, post: Dict):
        """Process a single post"""
        post_id = post.get('id')
        
        # Skip if already processed
        if post_id in self.processed_posts:
            print(f"[SKIP] Post {post_id} already processed")
            return
        
        print(f"\n{'='*80}")
        print(f"NEW POST DETECTED at {post['timestamp']}")
        print(f"{'='*80}")
        
        # Get post content
        content = post.get('content', '').strip()
        
        # Check if post is empty or too short
        if not content or len(content) < 2:
            print(f"[SKIP] Post content is empty or too short (length: {len(content)})")
            print("[INFO] Not processing empty post")
            # Still mark as processed to avoid checking again
            self.processed_posts.add(post_id)
            self.save_state()
            return
        
        print(f"Content: {content[:200]}...")
        print(f"Link: {post['link']}")
        
        # Analyze post
        print("\n[INFO] Analyzing post...")
        analysis = self.analyzer.analyze_post(post)
        
        print(f"Sentiment: {analysis['sentiment']['label'].upper()} "
              f"(polarity: {analysis['sentiment']['polarity']:.2f})")
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
            self.email_notifier.send_analysis_report(post, analysis, ideas)
        elif self.email_notifier.enabled and not should_send_email:
            print("\n[SKIP] Post not significant enough for email notification")
            print(f"       Market relevance: {analysis['market_relevance']:.2f}")
            print(f"       Companies found: {len(analysis['companies'])}")
            print(f"       Trading ideas: {len(ideas)}")
        
        # Mark as processed
        self.processed_posts.add(post_id)
        print(f"[OK] Post {post_id} processed and marked")
    
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
    
    def run_once(self):
        """Run one check cycle"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for new posts...")
        
        try:
            new_posts = self.scraper.get_new_posts()
            
            if new_posts:
                print(f"Found {len(new_posts)} new post(s)!")
                for post in new_posts:
                    self.process_post(post)
                
                # Save state after processing
                self.save_state()
            else:
                print("No new posts found.")
        
        except Exception as e:
            print(f"Error during check: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run the monitor continuously"""
        print("="*80)
        print("TRUMP TRUTH SOCIAL TRADING MONITOR")
        print("="*80)
        print(f"Monitoring interval: {self.check_interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        # Test connection
        print("Testing connection to trumpstruth.org...")
        if self.scraper.test_connection():
            print("✓ Connection successful\n")
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
            print("\n\n🛑 Stopping monitor...")
            self.save_state()
            print("State saved. Goodbye!")
    
    def stop(self):
        """Stop the monitor"""
        self.running = False


def main():
    # Get check interval from env or use default
    check_interval = int(os.getenv('CHECK_INTERVAL_SECONDS', 60))
    
    # Create and run monitor
    monitor = TruthTradingMonitor(check_interval=check_interval)
    monitor.run()


if __name__ == "__main__":
    main()

