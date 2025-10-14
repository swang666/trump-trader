"""
ARK Trade Analyzer

Analyzes ARK Invest trades and generates trading signals based on:
- Trade direction (buy/sell)
- Trade size relative to ETF holdings
- Historical patterns of ARK's performance
- Sector/company focus
"""

from typing import Dict, List
from datetime import datetime


class ARKTradeAnalyzer:
    def __init__(self):
        # Thresholds for significance
        self.significant_etf_percent = 0.15  # 0.15% of fund is considered significant
        self.large_share_threshold = 100000  # 100K+ shares is large
        
    def analyze_trade(self, trade: Dict) -> Dict:
        """
        Analyze a single ARK trade and generate insights
        
        Args:
            trade: Normalized trade dictionary
            
        Returns:
            Analysis dictionary with sentiment, confidence, and insights
        """
        direction = trade.get('direction', '').lower()
        shares = trade.get('shares', 0)
        etf_percent = trade.get('etf_percent', 0)
        ticker = trade.get('ticker', '')
        company = trade.get('company', '')
        fund = trade.get('fund', '')
        
        # Determine sentiment based on direction
        if direction == 'buy':
            sentiment = 'bullish'
            sentiment_score = 0.75
        elif direction == 'sell':
            sentiment = 'bearish'
            sentiment_score = -0.75
        else:
            sentiment = 'neutral'
            sentiment_score = 0.0
        
        # Calculate confidence based on trade size
        confidence = self._calculate_confidence(shares, etf_percent)
        
        # Determine urgency
        urgency = self._determine_urgency(shares, etf_percent)
        
        # Calculate market relevance (always high for ARK trades)
        market_relevance = self._calculate_market_relevance(shares, etf_percent, fund)
        
        # Generate insights
        insights = self._generate_insights(trade, confidence, sentiment)
        risk_factors = self._generate_risk_factors(trade, direction)
        
        # Build analysis
        analysis = {
            'id': trade['id'],
            'source': 'ARK_INVEST',
            'timestamp': trade['timestamp'],
            'content_preview': trade['content'][:200],
            
            # Sentiment analysis
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            
            # Trade details
            'companies': [{
                'name': company,
                'ticker': ticker,
                'sentiment': sentiment,
                'reason': f"ARK {direction.upper()}: {shares:,} shares ({etf_percent:.2f}% of {fund})"
            }],
            
            # Sectors - infer from fund type
            'sectors': self._infer_sectors(fund),
            
            # Topics
            'topics': [
                f'ARK {fund} Trading Activity',
                f'Cathie Wood {direction.capitalize()}',
                company,
                ticker
            ],
            
            # Metrics
            'urgency': urgency,
            'confidence': confidence,
            'market_relevance': market_relevance,
            
            # AI insights
            'ai_insights': insights,
            'risk_factors': risk_factors,
            
            # Metadata
            'trade_direction': direction,
            'trade_shares': shares,
            'trade_fund': fund,
            'trade_etf_percent': etf_percent,
            'trader': 'Cathie Wood (ARK Invest)'
        }
        
        return analysis
    
    def _calculate_confidence(self, shares: int, etf_percent: float) -> str:
        """Calculate confidence level based on trade size"""
        if etf_percent >= 0.5 or shares >= 500000:
            return 'high'
        elif etf_percent >= 0.15 or shares >= 100000:
            return 'medium'
        else:
            return 'low'
    
    def _determine_urgency(self, shares: int, etf_percent: float) -> str:
        """Determine urgency based on trade significance"""
        if etf_percent >= 0.5 or shares >= 500000:
            return 'high'
        elif etf_percent >= 0.15 or shares >= 100000:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_market_relevance(self, shares: int, etf_percent: float, fund: str) -> float:
        """Calculate market relevance score (0.0 to 1.0)"""
        # Base relevance for ARK trades
        base_relevance = 0.6
        
        # Boost for significant trades
        if etf_percent >= 0.5:
            base_relevance += 0.3
        elif etf_percent >= 0.15:
            base_relevance += 0.2
        
        # Boost for ARKK (flagship fund)
        if fund == 'ARKK':
            base_relevance += 0.1
        
        return min(base_relevance, 1.0)
    
    def _infer_sectors(self, fund: str) -> List[str]:
        """Infer sectors based on ARK fund type"""
        fund_sectors = {
            'ARKK': ['Innovation', 'Technology', 'Disruptive Innovation'],
            'ARKG': ['Genomics', 'Healthcare', 'Biotechnology'],
            'ARKW': ['Internet', 'Technology', 'Web 3.0'],
            'ARKF': ['Fintech', 'Financial Services', 'Payments'],
            'ARKQ': ['Autonomous Technology', 'Robotics', 'AI'],
            'ARKX': ['Space Exploration', 'Aerospace', 'Defense']
        }
        return fund_sectors.get(fund, ['Technology'])
    
    def _generate_insights(self, trade: Dict, confidence: str, sentiment: str) -> str:
        """Generate AI-like insights for the trade"""
        direction = trade.get('direction', '')
        ticker = trade.get('ticker', '')
        company = trade.get('company', '')
        shares = trade.get('shares', 0)
        etf_percent = trade.get('etf_percent', 0)
        fund = trade.get('fund', '')
        
        if direction == 'buy':
            action = 'bullish signal'
            interpretation = f"indicates conviction in {ticker}'s growth potential"
        else:
            action = 'bearish signal'
            interpretation = f"suggests profit-taking or reduced conviction in {ticker}"
        
        insight = f"Cathie Wood's {fund} {direction} of {shares:,} shares ({etf_percent:.2f}% of fund) "
        insight += f"provides a {confidence} confidence {action} for {company}. "
        insight += f"This {interpretation} within the ARK portfolio. "
        
        if etf_percent >= 0.5:
            insight += "The substantial position size indicates this is a high-conviction move."
        elif etf_percent >= 0.15:
            insight += "The meaningful position size suggests this is a significant strategic decision."
        
        return insight
    
    def _generate_risk_factors(self, trade: Dict, direction: str) -> str:
        """Generate risk factors for the trade"""
        risks = []
        
        if direction == 'buy':
            risks.append("ARK's high-growth focus means increased volatility risk")
            risks.append("Following institutional trades may result in poor entry timing if already priced in")
        else:
            risks.append("ARK sells don't always indicate fundamental weakness - could be rebalancing")
            risks.append("Short-selling based on ARK sells could be risky if fundamentals remain strong")
        
        risks.append("ARK's performance has been volatile - historical returns don't guarantee future results")
        risks.append("Individual trade significance may be overstated without full portfolio context")
        
        return " | ".join(risks)


if __name__ == "__main__":
    # Test the analyzer
    print("=" * 80)
    print("ARK Trade Analyzer Test")
    print("=" * 80)
    
    # Sample trades
    sample_trades = [
        {
            'id': 'ark_test_1',
            'source': 'ARK_INVEST',
            'timestamp': datetime.now().isoformat(),
            'date': '2024-01-15',
            'fund': 'ARKK',
            'ticker': 'TSLA',
            'company': 'Tesla Inc',
            'direction': 'buy',
            'shares': 150000,
            'etf_percent': 0.52,
            'content': 'Cathie Wood\'s ARKK bought 150K shares of TSLA (Tesla Inc)',
            'trader': 'Cathie Wood (ARK Invest)'
        },
        {
            'id': 'ark_test_2',
            'source': 'ARK_INVEST',
            'timestamp': datetime.now().isoformat(),
            'date': '2024-01-15',
            'fund': 'ARKG',
            'ticker': 'CRSP',
            'company': 'CRISPR Therapeutics',
            'direction': 'sell',
            'shares': 50000,
            'etf_percent': 0.18,
            'content': 'Cathie Wood\'s ARKG sold 50K shares of CRSP (CRISPR Therapeutics)',
            'trader': 'Cathie Wood (ARK Invest)'
        }
    ]
    
    analyzer = ARKTradeAnalyzer()
    
    for i, trade in enumerate(sample_trades, 1):
        print(f"\n{'='*80}")
        print(f"TRADE {i}: {trade['ticker']} - {trade['direction'].upper()}")
        print(f"{'='*80}")
        
        analysis = analyzer.analyze_trade(trade)
        
        print(f"Company: {analysis['companies'][0]['name']} ({analysis['companies'][0]['ticker']})")
        print(f"Sentiment: {analysis['sentiment'].upper()} (score: {analysis['sentiment_score']:.2f})")
        print(f"Confidence: {analysis['confidence'].upper()}")
        print(f"Urgency: {analysis['urgency'].upper()}")
        print(f"Market Relevance: {analysis['market_relevance']:.2f}")
        print(f"Sectors: {', '.join(analysis['sectors'])}")
        print(f"\nInsights: {analysis['ai_insights']}")
        print(f"\nRisk Factors: {analysis['risk_factors']}")

