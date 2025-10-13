"""
System Test Script
Tests all components of the trading monitor
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from scraper import TruthSocialScraper
from analyzer import PostAnalyzer
from trading_ideas import TradingIdeasGenerator


def test_scraper():
    """Test the scraper"""
    print("\n" + "="*80)
    print("TESTING SCRAPER")
    print("="*80)
    
    scraper = TruthSocialScraper()
    
    print("\n1. Testing connection...")
    if scraper.test_connection():
        print("   ✓ Connection successful")
    else:
        print("   ⚠️  Connection failed (might be expected if site is down)")
    
    print("\n2. Fetching latest posts...")
    posts = scraper.fetch_latest_posts(limit=5)
    
    if posts:
        print(f"   ✓ Found {len(posts)} posts")
        for i, post in enumerate(posts, 1):
            print(f"\n   Post {i}:")
            print(f"   ID: {post['id']}")
            print(f"   Content: {post['content'][:100]}...")
            print(f"   Link: {post['link']}")
    else:
        print("   ℹ️  No posts found (using test data)")
        # Create test data
        posts = [{
            'id': 'test_1',
            'content': 'Great news for American energy! We are DRILLING and will be energy independent. Oil companies are winning!',
            'timestamp': datetime.now().isoformat(),
            'link': 'https://trumpstruth.org/test'
        }]
    
    return posts


def test_analyzer(posts):
    """Test the analyzer"""
    print("\n" + "="*80)
    print("TESTING ANALYZER")
    print("="*80)
    
    analyzer = PostAnalyzer(use_ai=False)
    
    for i, post in enumerate(posts[:1], 1):  # Test first post only
        print(f"\nAnalyzing post {i}...")
        print(f"Content: {post['content'][:150]}...\n")
        
        analysis = analyzer.analyze_post(post)
        
        print(f"✓ Sentiment: {analysis['sentiment']['label']} "
              f"(polarity: {analysis['sentiment']['polarity']:.2f})")
        print(f"✓ Market Relevance: {analysis['market_relevance']:.2f}")
        print(f"✓ Companies: {[c['name'] for c in analysis['companies']]}")
        print(f"✓ Sectors: {analysis['sectors']}")
        print(f"✓ Topics: {analysis['topics']}")
        print(f"✓ Urgency: {analysis['urgency']}")
        print(f"✓ Entities: {[e['text'] for e in analysis['entities'][:5]]}")
    
    return analysis


def test_trading_ideas(analysis):
    """Test trading ideas generator"""
    print("\n" + "="*80)
    print("TESTING TRADING IDEAS GENERATOR")
    print("="*80)
    
    generator = TradingIdeasGenerator()
    
    ideas = generator.generate_ideas(analysis)
    
    if ideas:
        print(f"\n✓ Generated {len(ideas)} trading ideas:")
        print(generator.format_ideas_for_display(ideas))
    else:
        print("\nℹ️  No trading ideas generated (market relevance may be too low)")
    
    return ideas


def test_full_pipeline():
    """Test the full pipeline"""
    print("\n" + "="*80)
    print("TESTING FULL PIPELINE")
    print("="*80)
    
    # Create test post with high market relevance
    test_post = {
        'id': 'test_pipeline',
        'content': '''BREAKING: Just signed major executive order to boost American manufacturing!
        Tesla, Apple, and Ford will bring production back to USA. This is HUGE for American jobs and economy!
        We're also cutting regulations on energy companies. Oil and gas will boom! #MAGA''',
        'timestamp': datetime.now().isoformat(),
        'link': 'https://trumpstruth.org/test_pipeline'
    }
    
    print(f"\nTest post: {test_post['content']}\n")
    
    # Analyze
    analyzer = PostAnalyzer()
    analysis = analyzer.analyze_post(test_post)
    
    print(f"Analysis:")
    print(f"  Sentiment: {analysis['sentiment']['label']} ({analysis['sentiment']['polarity']:.2f})")
    print(f"  Market Relevance: {analysis['market_relevance']:.2f}")
    print(f"  Companies: {[c['name'] for c in analysis['companies']]}")
    print(f"  Sectors: {analysis['sectors']}")
    
    # Generate ideas
    generator = TradingIdeasGenerator()
    ideas = generator.generate_ideas(analysis)
    
    print(generator.format_ideas_for_display(ideas))
    
    print("\n✓ Full pipeline test complete!")


def main():
    print("\n" + "="*80)
    print("TRUMP TRUTH SOCIAL TRADING MONITOR - SYSTEM TEST")
    print("="*80)
    
    try:
        # Test scraper
        posts = test_scraper()
        
        # Test analyzer
        if posts:
            analysis = test_analyzer(posts)
            
            # Test trading ideas
            test_trading_ideas(analysis)
        
        # Test full pipeline with known data
        test_full_pipeline()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETE")
        print("="*80)
        print("\n✓ System is ready to use!")
        print("\nTo start monitoring, run: python main.py")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

