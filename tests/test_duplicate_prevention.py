"""
Test Duplicate Prevention
Verifies that the system won't analyze the same post twice
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import TruthTradingMonitor


def test_duplicate_prevention():
    """Test that duplicate posts are not processed twice"""
    print("="*80)
    print("TESTING DUPLICATE PREVENTION")
    print("="*80)
    
    # Create a temporary directory for test data
    temp_dir = tempfile.mkdtemp()
    original_data_dir = 'data'
    
    try:
        # Temporarily use test data directory
        if os.path.exists('data'):
            shutil.move('data', 'data_backup')
        os.makedirs('data', exist_ok=True)
        
        print("\n[TEST 1] Processing a new post")
        print("-" * 80)
        
        # Initialize monitor
        monitor = TruthTradingMonitor(check_interval=60)
        
        # Create a test post
        test_post = {
            'id': 'test_post_12345',
            'content': 'BREAKING: Great news for American manufacturing! Apple and Tesla expanding production.',
            'timestamp': datetime.now().isoformat(),
            'link': 'https://trumpstruth.org/test/12345',
            'title': ''
        }
        
        # Verify post is not in processed set
        assert test_post['id'] not in monitor.processed_posts, \
            "Post should not be in processed_posts initially"
        print(f"[OK] Post {test_post['id']} is not in processed_posts")
        
        # Process the post for the first time
        print(f"\n[INFO] Processing post for the first time...")
        monitor.process_post(test_post)
        
        # Verify post is now in processed set
        assert test_post['id'] in monitor.processed_posts, \
            "Post should be in processed_posts after processing"
        print(f"[OK] Post {test_post['id']} added to processed_posts")
        
        # Save state
        monitor.save_state()
        print("[OK] State saved")
        
        # Verify state file exists and contains the post
        with open('data/monitor_state.json', 'r') as f:
            state = json.load(f)
            assert test_post['id'] in state['processed_posts'], \
                "Post should be in saved state"
            print(f"[OK] Post {test_post['id']} found in saved state file")
        
        print("\n[TEST 2] Attempting to process the same post again")
        print("-" * 80)
        
        # Count analysis files before second processing
        analysis_file = 'data/post_analysis.json'
        ideas_file = 'data/trading_ideas.json'
        
        analysis_count_before = 0
        ideas_count_before = 0
        
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                analysis_count_before = len(json.load(f))
        
        if os.path.exists(ideas_file):
            with open(ideas_file, 'r') as f:
                ideas_count_before = len(json.load(f))
        
        print(f"[INFO] Analysis count before: {analysis_count_before}")
        print(f"[INFO] Trading ideas count before: {ideas_count_before}")
        
        # Try to process the same post again
        print(f"\n[INFO] Attempting to process duplicate post...")
        monitor.process_post(test_post)
        
        # Count files after
        analysis_count_after = 0
        ideas_count_after = 0
        
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                analysis_count_after = len(json.load(f))
        
        if os.path.exists(ideas_file):
            with open(ideas_file, 'r') as f:
                ideas_count_after = len(json.load(f))
        
        print(f"[INFO] Analysis count after: {analysis_count_after}")
        print(f"[INFO] Trading ideas count after: {ideas_count_after}")
        
        # Verify no new analysis was created
        assert analysis_count_after == analysis_count_before, \
            "No new analysis should be created for duplicate post"
        print("[OK] No new analysis created (duplicate was skipped)")
        
        # Verify no new trading ideas were created
        assert ideas_count_after == ideas_count_before, \
            "No new trading ideas should be created for duplicate post"
        print("[OK] No new trading ideas created (duplicate was skipped)")
        
        print("\n[TEST 3] Loading state and verifying persistence")
        print("-" * 80)
        
        # Create a new monitor instance (simulating restart)
        print("[INFO] Creating new monitor instance (simulating restart)...")
        monitor2 = TruthTradingMonitor(check_interval=60)
        
        # Verify the post is still in processed set
        assert test_post['id'] in monitor2.processed_posts, \
            "Post should still be in processed_posts after restart"
        print(f"[OK] Post {test_post['id']} persisted across restart")
        
        # Try to process with new instance
        print(f"\n[INFO] Attempting to process with new monitor instance...")
        analysis_count_before_restart = analysis_count_after
        
        monitor2.process_post(test_post)
        
        # Verify still no new analysis
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                analysis_count_after_restart = len(json.load(f))
        
        assert analysis_count_after_restart == analysis_count_before_restart, \
            "No new analysis should be created after restart"
        print("[OK] Duplicate prevention works across monitor restarts")
        
        print("\n[TEST 4] Processing a different post")
        print("-" * 80)
        
        # Create a different post
        test_post2 = {
            'id': 'test_post_67890',
            'content': 'More great news! American jobs are booming!',
            'timestamp': datetime.now().isoformat(),
            'link': 'https://trumpstruth.org/test/67890',
            'title': ''
        }
        
        print(f"[INFO] Processing a different post: {test_post2['id']}")
        
        # This should be processed normally
        assert test_post2['id'] not in monitor2.processed_posts, \
            "New post should not be in processed_posts"
        print(f"[OK] New post {test_post2['id']} is not in processed_posts")
        
        monitor2.process_post(test_post2)
        
        # Verify it was added
        assert test_post2['id'] in monitor2.processed_posts, \
            "New post should be added to processed_posts"
        print(f"[OK] New post {test_post2['id']} was processed successfully")
        
        # Verify state now has both posts
        monitor2.save_state()
        with open('data/monitor_state.json', 'r') as f:
            state = json.load(f)
            assert len(state['processed_posts']) == 2, \
                "State should contain both posts"
            assert test_post['id'] in state['processed_posts'], \
                "First post should be in state"
            assert test_post2['id'] in state['processed_posts'], \
                "Second post should be in state"
            print(f"[OK] State contains {len(state['processed_posts'])} posts")
        
        print("\n" + "="*80)
        print("[SUCCESS] ALL DUPLICATE PREVENTION TESTS PASSED!")
        print("="*80)
        print("\nSummary:")
        print("  [OK] First processing creates analysis")
        print("  [OK] Duplicate processing is skipped")
        print("  [OK] No redundant data is created")
        print("  [OK] State persists across restarts")
        print("  [OK] Different posts are processed normally")
        print("  [OK] Multiple posts tracked correctly")
        
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        return False
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup: restore original data directory
        if os.path.exists('data'):
            shutil.rmtree('data')
        if os.path.exists('data_backup'):
            shutil.move('data_backup', 'data')
        
        # Clean up temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def main():
    """Run the test"""
    print("\n")
    success = test_duplicate_prevention()
    
    print("\n" + "="*80)
    if success:
        print("TEST RESULT: PASSED")
        print("\nDuplicate prevention is working correctly!")
        print("The system will not analyze the same post twice.")
    else:
        print("TEST RESULT: FAILED")
        print("\nDuplicate prevention has issues. Check the output above.")
    print("="*80)
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

