"""
Trading Ideas Generator
Generates actionable trading ideas based on post analysis
"""

from typing import Dict, List
from datetime import datetime
import json


class TradingIdeasGenerator:
    """Generates trading ideas from analyzed posts"""
    
    def __init__(self):
        # Stock ticker mappings
        self.company_tickers = {
            'tesla': 'TSLA',
            'apple': 'AAPL',
            'amazon': 'AMZN',
            'google': 'GOOGL',
            'meta': 'META',
            'microsoft': 'MSFT',
            'nvidia': 'NVDA',
            'boeing': 'BA',
            'ford': 'F',
            'gm': 'GM',
            'truth_social': 'DJT',  # Trump Media & Technology Group
            'oil': 'XLE',  # Energy sector ETF
            'banks': 'XLF',  # Financial sector ETF
            'pharma': 'XLV',  # Healthcare sector ETF
        }
        
        self.sector_etfs = {
            'energy': ['XLE', 'XOP', 'OIH'],
            'tech': ['XLK', 'QQQ', 'SOXX'],
            'defense': ['ITA', 'XAR', 'PPA'],
            'manufacturing': ['XLI', 'VIS'],
            'crypto': ['BITO', 'COIN'],
            'real_estate': ['VNQ', 'IYR'],
            'healthcare': ['XLV', 'IHI', 'IBB'],
        }
    
    def generate_ideas(self, analysis: Dict) -> List[Dict]:
        """
        Generate trading ideas from post analysis
        
        Args:
            analysis: Analysis dictionary from PostAnalyzer
            
        Returns:
            List of trading idea dictionaries
        """
        ideas = []
        
        # Skip if not market relevant
        if analysis['market_relevance'] < 0.2:
            return ideas
        
        # Generate ideas for mentioned companies
        for company in analysis['companies']:
            idea = self._generate_company_idea(company, analysis)
            if idea:
                ideas.append(idea)
        
        # Generate ideas for sectors
        for sector in analysis['sectors']:
            idea = self._generate_sector_idea(sector, analysis)
            if idea:
                ideas.append(idea)
        
        # Generate thematic ideas
        thematic_ideas = self._generate_thematic_ideas(analysis)
        ideas.extend(thematic_ideas)
        
        # Add metadata to all ideas
        for idea in ideas:
            idea['post_id'] = analysis['post_id']
            idea['timestamp'] = datetime.now().isoformat()
            idea['source_content'] = analysis['content_preview']
        
        return ideas
    
    def _generate_company_idea(self, company: Dict, analysis: Dict) -> Dict:
        """Generate trading idea for a specific company"""
        company_name = company.get('name', '')
        
        # AI provides ticker directly, or fallback to mapping
        ticker = company.get('ticker') or self.company_tickers.get(company_name, None)
        
        if not ticker:
            return None
        
        sentiment = company.get('sentiment', 'neutral')
        overall_sentiment = analysis.get('sentiment', {}).get('label', 'neutral')
        urgency = analysis.get('urgency', 'low')
        
        # Determine direction
        if sentiment == 'positive':
            direction = 'long'
            action = 'Buy'
            confidence = 'medium'
        elif sentiment == 'negative':
            direction = 'short'
            action = 'Sell/Short'
            confidence = 'medium'
        else:
            return None
        
        # Adjust confidence based on urgency and overall sentiment
        if urgency == 'high':
            confidence = 'high'
        elif overall_sentiment != sentiment:
            confidence = 'low'
        
        # Generate rationale
        reason = company.get('reason', '')
        rationale = reason if reason else self._generate_rationale(company_name, sentiment, '')
        
        # Determine timeframe
        timeframe = self._determine_timeframe(urgency)
        
        return {
            'type': 'company',
            'ticker': ticker,
            'name': company_name,
            'action': action,
            'direction': direction,
            'confidence': confidence,
            'timeframe': timeframe,
            'rationale': rationale,
            'urgency': urgency,
            'risk_level': self._assess_risk(sentiment, confidence)
        }
    
    def _generate_sector_idea(self, sector: str, analysis: Dict) -> Dict:
        """Generate trading idea for a sector"""
        etfs = self.sector_etfs.get(sector, [])
        
        if not etfs:
            return None
        
        sentiment = analysis['sentiment']['label']
        urgency = analysis['urgency']
        
        if sentiment == 'neutral':
            return None
        
        direction = 'long' if sentiment == 'positive' else 'short'
        action = 'Buy' if sentiment == 'positive' else 'Sell/Short'
        
        # Confidence based on market relevance and urgency
        if analysis['market_relevance'] > 0.5 and urgency == 'high':
            confidence = 'high'
        elif analysis['market_relevance'] > 0.3:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        timeframe = self._determine_timeframe(urgency)
        
        return {
            'type': 'sector',
            'ticker': etfs[0],  # Primary ETF
            'alternatives': etfs[1:],
            'sector': sector,
            'action': action,
            'direction': direction,
            'confidence': confidence,
            'timeframe': timeframe,
            'rationale': f"{sentiment.capitalize()} sentiment on {sector} sector based on post content",
            'urgency': urgency,
            'risk_level': self._assess_risk(sentiment, confidence)
        }
    
    def _generate_thematic_ideas(self, analysis: Dict) -> List[Dict]:
        """Generate thematic trading ideas based on topics"""
        ideas = []
        topics = analysis['topics']
        sentiment = analysis['sentiment']['label']
        
        if 'trade' in topics:
            # Trade policy implications
            if 'negative' in sentiment and any('china' in t.lower() for t in analysis.get('key_phrases', [])):
                ideas.append({
                    'type': 'theme',
                    'ticker': 'FXI',  # China Large-Cap ETF
                    'name': 'China Trade Tensions',
                    'action': 'Sell/Short',
                    'direction': 'short',
                    'confidence': 'medium',
                    'timeframe': 'short-term',
                    'rationale': 'Negative China trade rhetoric suggests potential market pressure on Chinese equities',
                    'urgency': analysis['urgency'],
                    'risk_level': 'high'
                })
        
        if 'tax' in topics:
            # Tax policy implications
            if sentiment == 'positive':
                ideas.append({
                    'type': 'theme',
                    'ticker': 'SPY',
                    'name': 'Tax Policy',
                    'action': 'Buy',
                    'direction': 'long',
                    'confidence': 'low',
                    'timeframe': 'medium-term',
                    'rationale': 'Positive tax policy discussion could benefit broad market',
                    'urgency': analysis['urgency'],
                    'risk_level': 'medium'
                })
        
        if 'regulation' in topics:
            # Deregulation benefits
            if sentiment == 'positive':
                ideas.append({
                    'type': 'theme',
                    'ticker': 'XLI',  # Industrial sector
                    'name': 'Deregulation',
                    'action': 'Buy',
                    'direction': 'long',
                    'confidence': 'medium',
                    'timeframe': 'medium-term',
                    'rationale': 'Deregulation typically benefits industrial and manufacturing sectors',
                    'urgency': analysis['urgency'],
                    'risk_level': 'medium'
                })
        
        return ideas
    
    def _generate_rationale(self, company: str, sentiment: str, context: str) -> str:
        """Generate human-readable rationale"""
        if sentiment == 'positive':
            return f"Positive mention of {company} suggests potential upside. Context: {context[:80]}..."
        elif sentiment == 'negative':
            return f"Negative mention of {company} suggests potential downside. Context: {context[:80]}..."
        else:
            return f"Neutral mention of {company}. Context: {context[:80]}..."
    
    def _determine_timeframe(self, urgency: str) -> str:
        """Determine trading timeframe based on urgency"""
        if urgency == 'high':
            return 'short-term'  # Days to 1-2 weeks
        elif urgency == 'medium':
            return 'medium-term'  # 2-8 weeks
        else:
            return 'long-term'  # Months
    
    def _assess_risk(self, sentiment: str, confidence: str) -> str:
        """Assess risk level of the trade"""
        if confidence == 'low':
            return 'high'
        elif confidence == 'high' and sentiment in ['positive', 'negative']:
            return 'medium'
        else:
            return 'medium-high'
    
    def format_ideas_for_display(self, ideas: List[Dict]) -> str:
        """Format trading ideas for console display"""
        if not ideas:
            return "No trading ideas generated."
        
        output = f"\n{'='*80}\n"
        output += f"TRADING IDEAS ({len(ideas)} ideas)\n"
        output += f"{'='*80}\n\n"
        
        for i, idea in enumerate(ideas, 1):
            output += f"{i}. {idea['action']} {idea['ticker']}"
            if 'name' in idea:
                output += f" ({idea['name']})"
            output += f"\n"
            output += f"   Type: {idea['type'].upper()} | "
            output += f"Confidence: {idea['confidence'].upper()} | "
            output += f"Risk: {idea['risk_level'].upper()}\n"
            output += f"   Timeframe: {idea['timeframe']}\n"
            output += f"   Rationale: {idea['rationale']}\n"
            if 'alternatives' in idea:
                output += f"   Alternatives: {', '.join(idea['alternatives'])}\n"
            output += f"\n"
        
        return output
    
    def save_ideas(self, ideas: List[Dict], filepath: str = "data/trading_ideas.json"):
        """Save trading ideas to JSON file"""
        try:
            # Load existing ideas
            try:
                with open(filepath, 'r') as f:
                    existing = json.load(f)
            except FileNotFoundError:
                existing = []
            
            # Append new ideas
            existing.extend(ideas)
            
            # Save back
            with open(filepath, 'w') as f:
                json.dump(existing, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving ideas: {e}")
            return False


def main():
    """Test the trading ideas generator"""
    from analyzer import PostAnalyzer
    
    analyzer = PostAnalyzer()
    generator = TradingIdeasGenerator()
    
    # Test post
    test_post = {
        'id': 'test_1',
        'content': 'Just announced a major new trade deal with China! Great for American manufacturing and jobs. Tesla and Apple will benefit tremendously. This is a WIN for America!',
        'timestamp': datetime.now().isoformat()
    }
    
    print("Analyzing post and generating trading ideas...\n")
    
    analysis = analyzer.analyze_post(test_post)
    ideas = generator.generate_ideas(analysis)
    
    print(generator.format_ideas_for_display(ideas))


if __name__ == "__main__":
    main()

