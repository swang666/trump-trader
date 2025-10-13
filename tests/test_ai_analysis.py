"""
Test AI-Powered Analysis
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from analyzer import PostAnalyzer
from trading_ideas import TradingIdeasGenerator


def main():
    print("="*80)
    print("TESTING AI-POWERED ANALYSIS")
    print("="*80)
    
    analyzer = PostAnalyzer()
    generator = TradingIdeasGenerator()
    
    # Test post with multiple companies
    test_post = {
        'id': 'test_1',
        'content': '''BREAKING: Just had a great meeting with Tim Cook! 
        Apple is bringing iPhone manufacturing back to America. 
        Also spoke with Elon about Tesla's new Gigafactory in Texas. 
        This is HUGE for American jobs and the economy! 
        American manufacturing is BOOMING! #MAGA''',
        'timestamp': datetime.now().isoformat()
    }
    
    print("\nTest Post:")
    print(test_post['content'])
    print("\n" + "="*80)
    
    # Analyze
    print("\nAnalyzing with Gemini AI...")
    analysis = analyzer.analyze_post(test_post)
    
    print("\nRESULTS:")
    print("-" * 80)
    print(f"Sentiment: {analysis['sentiment']['label']} ({analysis['sentiment']['polarity']:.2f})")
    print(f"Market Relevance: {analysis['market_relevance']:.2f}")
    print(f"Urgency: {analysis['urgency']}")
    print(f"Analysis Method: {analysis.get('analysis_method', 'unknown')}")
    
    if analysis['companies']:
        print(f"\nCompanies Detected ({len(analysis['companies'])}):")
        for company in analysis['companies']:
            print(f"  - {company.get('name', 'N/A')} ({company.get('ticker', 'N/A')})")
            print(f"    Sentiment: {company.get('sentiment', 'N/A')}")
            if company.get('reason'):
                print(f"    Reason: {company.get('reason', '')}")
    
    if analysis['sectors']:
        print(f"\nSectors: {', '.join(analysis['sectors'])}")
    
    if analysis['topics']:
        print(f"Topics: {', '.join(analysis['topics'])}")
    
    if analysis.get('ai_insights'):
        print(f"\nAI Insights:")
        print(f"  {analysis['ai_insights']}")
    
    if analysis.get('risk_factors'):
        print(f"\nRisk Factors:")
        print(f"  {analysis['risk_factors']}")
    
    # Generate trading ideas
    print("\n" + "="*80)
    print("GENERATING TRADING IDEAS")
    print("="*80)
    
    ideas = generator.generate_ideas(analysis)
    
    if ideas:
        print(f"\nGenerated {len(ideas)} trading ideas:\n")
        for i, idea in enumerate(ideas, 1):
            print(f"{i}. {idea['action']} {idea['ticker']}")
            if 'name' in idea:
                print(f"   Name: {idea['name']}")
            print(f"   Type: {idea['type'].upper()}")
            print(f"   Confidence: {idea['confidence'].upper()}")
            print(f"   Risk: {idea['risk_level'].upper()}")
            print(f"   Timeframe: {idea['timeframe']}")
            print(f"   Rationale: {idea['rationale'][:100]}...")
            print()
    else:
        print("\nNo trading ideas generated.")
    
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

