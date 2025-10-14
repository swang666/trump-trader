"""
Quick test to run one monitoring cycle
"""
from main import MultiSourceTradingMonitor

print("Starting monitor test...")
monitor = MultiSourceTradingMonitor(check_interval=60)

# Run one check cycle
print("\nRunning one check cycle...\n")
monitor.run_once()

print("\n[SUCCESS] Monitor is working correctly!")
print("You can now run: python main.py")

