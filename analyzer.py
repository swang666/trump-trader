"""
Post Analyzer
Analyzes Truth Social posts for market-relevant information
"""

import re
import logging
from typing import Dict, List, Optional
from textblob import TextBlob
import spacy
from datetime import datetime
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# Try to load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None


class PostAnalyzer:
    """Analyzes posts for trading signals and market sentiment"""
    
    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Initialize Gemini if available
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-pro')
                self.use_ai = True
                logger.info("Google Gemini AI enabled for analysis")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")
                logger.warning("Will use basic sentiment analysis only")
                self.gemini_model = None
                self.use_ai = False
        else:
            logger.warning("No GEMINI_API_KEY found - using basic analysis only")
            self.gemini_model = None
            self.use_ai = False
        
        self.sentiment_keywords = {
            'positive': ['great', 'wonderful', 'tremendous', 'fantastic', 'best', 'winning', 
                        'success', 'growth', 'strong', 'booming', 'excellent'],
            'negative': ['terrible', 'horrible', 'worst', 'disaster', 'failing', 'fake',
                        'bad', 'weak', 'crisis', 'problem', 'corrupt'],
            'action': ['announce', 'launch', 'introduce', 'sign', 'order', 'executive order',
                      'deal', 'agreement', 'policy', 'plan']
        }
    
    def analyze_post(self, post: Dict) -> Dict:
        """
        Analyze a post and extract trading-relevant information
        
        Args:
            post: Post dictionary with 'content' and other fields
            
        Returns:
            Analysis dictionary with sentiment, entities, and signals
        """
        content = post.get('content', '') + ' ' + post.get('title', '')
        
        # Use AI-powered analysis if available
        if self.use_ai and self.gemini_model:
            analysis = self._ai_powered_analysis(content, post)
        else:
            # Fallback to basic sentiment analysis
            analysis = self._basic_analysis(content, post)
        
        return analysis
    
    def _ai_powered_analysis(self, content: str, post: Dict) -> Dict:
        """Use Gemini AI to analyze the post comprehensively"""
        try:
            prompt = f"""Analyze this Truth Social post for stock trading signals.

POST: "{content}"

Provide your analysis in this EXACT JSON format (no markdown, just JSON):
{{
  "sentiment": {{
    "label": "positive/negative/neutral",
    "polarity": 0.0 to 1.0 or -1.0 to 0.0,
    "confidence": 0.0 to 1.0
  }},
  "companies": [
    {{
      "name": "company name",
      "ticker": "STOCK_SYMBOL",
      "sentiment": "positive/negative/neutral",
      "reason": "brief explanation"
    }}
  ],
  "sectors": ["sector1", "sector2"],
  "topics": ["topic1", "topic2"],
  "urgency": "high/medium/low",
  "market_relevance": 0.0 to 1.0,
  "key_insights": "Brief trading insight (2-3 sentences)",
  "risk_factors": "Key risks to consider"
}}

Rules:
- Only include companies if EXPLICITLY mentioned or clearly implied
- Include ticker symbols (e.g., TSLA, AAPL, XLE)
- Be specific with sentiment and reasons
- market_relevance: 0.0 = not relevant, 1.0 = very relevant
- urgency based on timing words like "breaking", "just announced", etc."""

            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            import json
            ai_data = json.loads(response_text)
            
            # Construct analysis with AI data
            analysis = {
                'post_id': post.get('id'),
                'timestamp': post.get('timestamp'),
                'content_preview': content[:200],
                'sentiment': ai_data.get('sentiment', {'label': 'neutral', 'polarity': 0.0, 'confidence': 0.5}),
                'companies': ai_data.get('companies', []),
                'sectors': ai_data.get('sectors', []),
                'topics': ai_data.get('topics', []),
                'urgency': ai_data.get('urgency', 'low'),
                'market_relevance': ai_data.get('market_relevance', 0.0),
                'ai_insights': ai_data.get('key_insights', ''),
                'risk_factors': ai_data.get('risk_factors', ''),
                'analysis_method': 'ai'
            }
            
            return analysis
            
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            logger.warning("Falling back to basic analysis...")
            return self._basic_analysis(content, post)
    
    def _basic_analysis(self, content: str, post: Dict) -> Dict:
        """Fallback basic analysis without AI"""
        analysis = {
            'post_id': post.get('id'),
            'timestamp': post.get('timestamp'),
            'content_preview': content[:200],
            'sentiment': self._analyze_sentiment(content),
            'companies': [],
            'sectors': [],
            'topics': [],
            'urgency': 'low',
            'market_relevance': 0.1,
            'ai_insights': 'Basic sentiment analysis only - add GEMINI_API_KEY for full analysis',
            'analysis_method': 'basic'
        }
        
        return analysis
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of the text"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classify sentiment
        if polarity > 0.1:
            sentiment_label = 'positive'
        elif polarity < -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'label': sentiment_label,
            'polarity': polarity,
            'subjectivity': subjectivity,
            'confidence': abs(polarity)
        }
    
    def _gemini_analysis(self, text: str) -> str:
        """Get advanced analysis from Google Gemini AI"""
        try:
            prompt = f"""You are a financial analyst analyzing social media posts for stock trading signals.

Analyze this Truth Social post for stock trading implications:

"{text}"

Provide a concise analysis (3-4 sentences) covering:
1. Key companies/sectors affected
2. Market sentiment (bullish/bearish)
3. Potential trading opportunities
4. Risk factors

Be specific and actionable."""
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Gemini AI analysis failed: {e}"


def main():
    """Test the analyzer"""
    analyzer = PostAnalyzer()
    
    # Test post
    test_post = {
        'id': 'test_1',
        'content': 'Just announced a major new trade deal with China! Great for American manufacturing and jobs. Tesla and Apple will benefit tremendously. This is a WIN for America!',
        'timestamp': datetime.now().isoformat()
    }
    
    print("Analyzing test post...")
    print(f"Content: {test_post['content']}\n")
    
    analysis = analyzer.analyze_post(test_post)
    
    print(f"Sentiment: {analysis['sentiment']['label']} (polarity: {analysis['sentiment']['polarity']:.2f})")
    print(f"Market Relevance: {analysis['market_relevance']:.2f}")
    print(f"Companies: {[c['name'] for c in analysis['companies']]}")
    print(f"Sectors: {analysis['sectors']}")
    print(f"Topics: {analysis['topics']}")
    print(f"Urgency: {analysis['urgency']}")


if __name__ == "__main__":
    main()

