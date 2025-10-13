"""
Test Runner
Runs all tests in the tests/ directory
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("="*80)
    print("TRUMP TRUTH SOCIAL TRADING MONITOR - TEST SUITE")
    print("="*80)
    print()
    
    tests = [
        ("Gemini API", "tests.test_gemini"),
        ("Email Notifications", "tests.test_email"),
        ("AI Analysis", "tests.test_ai_analysis"),
        ("Duplicate Prevention", "tests.test_duplicate_prevention"),
        ("Full System", "tests.test_system"),
    ]
    
    results = []
    
    for test_name, test_module in tests:
        print(f"\n{'='*80}")
        print(f"Running: {test_name}")
        print(f"{'='*80}\n")
        
        try:
            module = __import__(test_module, fromlist=['main'])
            if hasattr(module, 'main'):
                module.main()
                results.append((test_name, "PASSED"))
            else:
                print(f"[WARNING] No main() function found in {test_module}")
                results.append((test_name, "SKIPPED"))
        except KeyboardInterrupt:
            print(f"\n[INTERRUPTED] Test stopped by user")
            results.append((test_name, "INTERRUPTED"))
            break
        except Exception as e:
            print(f"\n[ERROR] Test failed: {e}")
            results.append((test_name, "FAILED"))
    
    # Print summary
    print(f"\n\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    for test_name, status in results:
        status_symbol = {
            "PASSED": "[OK]",
            "FAILED": "[FAIL]",
            "SKIPPED": "[SKIP]",
            "INTERRUPTED": "[STOP]"
        }.get(status, "[?]")
        print(f"{status_symbol} {test_name}: {status}")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Test runner failed: {e}")
        import traceback
        traceback.print_exc()

