"""
Test Email Notification Filtering
Verifies that insignificant posts don't trigger email notifications
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import TruthTradingMonitor


def test_email_filtering():
    """Test that only significant posts trigger email notifications"""
    print("="*80)
    print("TESTING EMAIL NOTIFICATION FILTERING")
    print("="*80)
    
    # Create temporary data directory
    if os.path.exists('data'):
        shutil.move('data', 'data_backup')
    os.makedirs('data', exist_ok=True)
    
    try:
        # Initialize monitor with mocked email
        monitor = TruthTradingMonitor(check_interval=60)
        
        # Mock the email notifier to track calls
        email_sent_count = [0]  # Use list to make it mutable in nested function
        original_send = monitor.email_notifier.send_analysis_report
        
        def mock_send(*args, **kwargs):
            email_sent_count[0] += 1
            print(f"[MOCK] Email would be sent (count: {email_sent_count[0]})")
            return True
        
        monitor.email_notifier.send_analysis_report = mock_send
        monitor.email_notifier.enabled = True  # Enable for testing
        
        print("\n[TEST 1] Empty post - should NOT send email")
        print("-" * 80)
        
        empty_post = {
            'id': 'test_empty',
            'content': '',
            'timestamp': datetime.now().isoformat(),
            'link': 'https://test.com/empty',
            'title': ''
        }
        
        monitor.process_post(empty_post)
        assert email_sent_count[0] == 0, "Empty post should not trigger email"
        print("[OK] Empty post did not trigger email")
        
        print("\n[TEST 2] Very short post (1 char) - should NOT send email")
        print("-" * 80)
        
        short_post = {
            'id': 'test_short',
            'content': 'H',
            'timestamp': datetime.now().isoformat(),
            'link': 'https://test.com/short',
            'title': ''
        }
        
        monitor.process_post(short_post)
        assert email_sent_count[0] == 0, "Single character post should not trigger email"
        print("[OK] Single character post did not trigger email")
        
        print("\n[TEST 3] Generic post with low relevance - should NOT send email")
        print("-" * 80)
        
        generic_post = {
            'id': 'test_generic',
            'content': 'Having a great day! The weather is wonderful and everything is fantastic!',
            'timestamp': datetime.now().isoformat(),
            'link': 'https://test.com/generic',
            'title': ''
        }
        
        monitor.process_post(generic_post)
        # This might or might not send depending on AI analysis
        initial_count = email_sent_count[0]
        print(f"[INFO] Generic post resulted in {email_sent_count[0]} emails")
        
        print("\n[TEST 4] Market-relevant post - SHOULD send email")
        print("-" * 80)
        
        relevant_post = {
            'id': 'test_relevant',
            'content': 'BREAKING: Just had a great meeting with Tim Cook! Apple is bringing iPhone manufacturing back to America. HUGE for jobs and the economy! Tesla also expanding production.',
            'timestamp': datetime.now().isoformat(),
            'link': 'https://test.com/relevant',
            'title': ''
        }
        
        before_relevant = email_sent_count[0]
        monitor.process_post(relevant_post)
        after_relevant = email_sent_count[0]
        
        assert after_relevant > before_relevant, "Relevant post should trigger email"
        print(f"[OK] Relevant post triggered email (before: {before_relevant}, after: {after_relevant})")
        
        print("\n[TEST 5] Verification of filtering criteria")
        print("-" * 80)
        
        # Test the filtering method directly
        test_cases = [
            {
                'name': 'High relevance with companies',
                'analysis': {
                    'market_relevance': 0.8,
                    'companies': [{'name': 'Apple', 'ticker': 'AAPL'}],
                    'content_preview': 'Apple is doing great things',
                    'urgency': 'medium'
                },
                'ideas': [{'ticker': 'AAPL'}],
                'should_send': True
            },
            {
                'name': 'Low relevance',
                'analysis': {
                    'market_relevance': 0.1,
                    'companies': [],
                    'content_preview': 'Having a nice day',
                    'urgency': 'low'
                },
                'ideas': [],
                'should_send': False
            },
            {
                'name': 'No companies, no ideas, low urgency',
                'analysis': {
                    'market_relevance': 0.5,
                    'companies': [],
                    'content_preview': 'General statement about politics',
                    'urgency': 'low'
                },
                'ideas': [],
                'should_send': False
            },
            {
                'name': 'High urgency compensates',
                'analysis': {
                    'market_relevance': 0.4,
                    'companies': [],
                    'content_preview': 'BREAKING: Major policy change',
                    'urgency': 'high'
                },
                'ideas': [],
                'should_send': True
            }
        ]
        
        for test_case in test_cases:
            result = monitor._should_send_email_notification(
                test_case['analysis'],
                test_case['ideas']
            )
            expected = test_case['should_send']
            
            status = "[OK]" if result == expected else "[FAIL]"
            print(f"{status} {test_case['name']}: "
                  f"should_send={expected}, got={result}")
            
            assert result == expected, f"Failed: {test_case['name']}"
        
        print("\n" + "="*80)
        print("[SUCCESS] ALL EMAIL FILTERING TESTS PASSED!")
        print("="*80)
        print("\nSummary:")
        print("  [OK] Empty posts do not trigger emails")
        print("  [OK] Short posts do not trigger emails")
        print("  [OK] Low relevance posts do not trigger emails")
        print("  [OK] Relevant posts DO trigger emails")
        print("  [OK] Filtering criteria work correctly")
        print(f"\nTotal emails that would be sent: {email_sent_count[0]}")
        
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        return False
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if os.path.exists('data'):
            shutil.rmtree('data')
        if os.path.exists('data_backup'):
            shutil.move('data_backup', 'data')


def main():
    """Run the test"""
    print("\n")
    success = test_email_filtering()
    
    print("\n" + "="*80)
    if success:
        print("TEST RESULT: PASSED")
        print("\nEmail filtering is working correctly!")
        print("Only significant posts will trigger email notifications.")
    else:
        print("TEST RESULT: FAILED")
        print("\nEmail filtering has issues. Check the output above.")
    print("="*80)
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

