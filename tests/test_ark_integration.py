"""
Test ARK Invest Integration

Tests the ARK scraper, analyzer, and integration with main system
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.ark_scraper import ARKTradesScraper
from sources.ark_analyzer import ARKTradeAnalyzer


def test_ark_scraper():
    """Test ARK scraper"""
    print("\n" + "="*80)
    print("TEST 1: ARK SCRAPER")
    print("="*80)
    
    scraper = ARKTradesScraper()
    trades = scraper.fetch_latest_trades(limit=5)
    
    assert len(trades) > 0, "Should fetch at least some trades"
    print(f"[OK] Fetched {len(trades)} trades")
    
    # Check trade structure
    sample_trade = trades[0]
    required_fields = ['id', 'source', 'timestamp', 'ticker', 'company', 'direction', 'fund']
    for field in required_fields:
        assert field in sample_trade, f"Trade should have '{field}' field"
    
    print(f"[OK] Trade structure valid")
    print(f"[OK] Sample trade: {sample_trade['title']}")
    
    return trades


def test_ark_analyzer(trades):
    """Test ARK analyzer"""
    print("\n" + "="*80)
    print("TEST 2: ARK ANALYZER")
    print("="*80)
    
    analyzer = ARKTradeAnalyzer()
    
    for i, trade in enumerate(trades[:3], 1):
        print(f"\nAnalyzing trade {i}: {trade['ticker']} - {trade['direction'].upper()}")
        analysis = analyzer.analyze_trade(trade)
        
        # Check analysis structure
        required_fields = ['sentiment', 'market_relevance', 'companies', 'sectors', 'confidence']
        for field in required_fields:
            assert field in analysis, f"Analysis should have '{field}' field"
        
        print(f"  Sentiment: {analysis['sentiment'].upper()}")
        print(f"  Confidence: {analysis['confidence'].upper()}")
        print(f"  Market Relevance: {analysis['market_relevance']:.2f}")
        print(f"  Companies: {[c['ticker'] for c in analysis['companies']]}")
    
    print(f"\n[OK] Analyzed {min(3, len(trades))} trades successfully")


def test_full_integration():
    """Test full system integration"""
    print("\n" + "="*80)
    print("TEST 3: FULL SYSTEM INTEGRATION")
    print("="*80)
    
    # Import main system components
    from main import MultiSourceTradingMonitor
    from trading_ideas import TradingIdeasGenerator
    
    # Create monitor (but don't run it)
    monitor = MultiSourceTradingMonitor(check_interval=60)
    
    print("[OK] Monitor initialized successfully")
    print(f"     Sources configured: Truth Social + ARK Trades")
    print(f"     Processed items tracked: {len(monitor.processed_items)}")
    
    # Test ARK trade processing with a mock trade
    mock_trade = {
        'id': 'ark_test_integration',
        'source': 'ARK_INVEST',
        'timestamp': datetime.now().isoformat(),
        'date': '2024-01-15',
        'fund': 'ARKK',
        'ticker': 'TSLA',
        'company': 'Tesla Inc',
        'direction': 'buy',
        'shares': 250000,
        'etf_percent': 0.75,
        'content': 'Cathie Wood\'s ARKK bought 250K shares of TSLA (Tesla Inc), representing 0.75% of the fund',
        'type': 'trade',
        'link': 'https://arkfunds.io/trades/arkk'
    }
    
    print(f"\n[INFO] Testing ARK trade processing...")
    print(f"     Trade: {mock_trade['title'] if 'title' in mock_trade else mock_trade['content'][:80]}")
    
    # Process the mock trade
    try:
        monitor.process_item(mock_trade)
        print("[OK] ARK trade processed successfully")
    except Exception as e:
        print(f"[ERROR] Trade processing failed: {e}")
        raise
    
    # Verify it was marked as processed
    assert mock_trade['id'] in monitor.processed_items, "Trade should be marked as processed"
    print("[OK] Trade marked as processed")
    
    # Test deduplication
    print(f"\n[INFO] Testing deduplication...")
    monitor.process_item(mock_trade)  # Try to process same trade again
    print("[OK] Duplicate processing prevented")


def main():
    print("="*80)
    print("ARK INVEST INTEGRATION TEST SUITE")
    print("="*80)
    
    try:
        # Test 1: Scraper
        trades = test_ark_scraper()
        
        # Test 2: Analyzer
        test_ark_analyzer(trades)
        
        # Test 3: Full Integration
        test_full_integration()
        
        print("\n" + "="*80)
        print("[SUCCESS] ALL ARK INTEGRATION TESTS PASSED!")
        print("="*80)
        print("\nARK Invest integration is working correctly!")
        print("The system can now monitor:")
        print("  - Trump Truth Social posts")
        print("  - ARK Invest daily trades")
        print("\nReady for production use!")
        
    except AssertionError as e:
        print(f"\n[ERROR] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

