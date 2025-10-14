"""
Email Notification System
Sends structured reports when new posts are analyzed
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


class EmailNotifier:
    """Sends email notifications with trading analysis reports"""
    
    def __init__(self):
        self.enabled = False
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        # Check if email is configured
        if self.sender_email and self.sender_password and self.recipient_email:
            self.enabled = True
            print("[OK] Email notifications enabled")
        else:
            print("[WARNING] Email not configured - notifications disabled")
            print("         Add SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL to .env")
    
    def send_analysis_report(self, post: Dict, analysis: Dict, trading_ideas: List[Dict]) -> bool:
        """
        Send email notification with analysis report
        
        Args:
            post: Original post data
            analysis: Analysis results
            trading_ideas: Generated trading ideas
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self._create_subject(analysis)
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Create plain text version
            text_content = self._create_text_report(post, analysis, trading_ideas)
            
            # Create HTML version
            html_content = self._create_html_report(post, analysis, trading_ideas)
            
            # Attach both versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"[OK] Email notification sent to {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
            return False
    
    def _create_subject(self, analysis: Dict) -> str:
        """Create email subject line"""
        # Handle both dict and string sentiment formats
        sentiment_data = analysis.get('sentiment', {})
        if isinstance(sentiment_data, dict):
            sentiment = sentiment_data.get('label', 'neutral').upper()
        else:
            sentiment = str(sentiment_data).upper() if sentiment_data else 'NEUTRAL'
        
        relevance = analysis.get('market_relevance', 0.0)
        urgency = analysis.get('urgency', 'low').upper()
        
        num_companies = len(analysis.get('companies', []))
        
        if num_companies > 0:
            return f"[{urgency}] Truth Social Alert: {sentiment} - {num_companies} Companies Mentioned"
        else:
            return f"[{urgency}] Truth Social Alert: {sentiment} Sentiment"
    
    def _create_text_report(self, post: Dict, analysis: Dict, trading_ideas: List[Dict]) -> str:
        """Create plain text version of report"""
        lines = []
        lines.append("=" * 80)
        lines.append("TRUMP TRUTH SOCIAL TRADING ALERT")
        lines.append("=" * 80)
        lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Post Link: {post.get('link', 'N/A')}")
        lines.append("")
        
        lines.append("POST CONTENT:")
        lines.append("-" * 80)
        content = post.get('content', '')[:500]
        lines.append(content)
        if len(post.get('content', '')) > 500:
            lines.append("... (truncated)")
        lines.append("")
        
        lines.append("ANALYSIS:")
        lines.append("-" * 80)
        sentiment = analysis.get('sentiment', {})
        lines.append(f"Sentiment: {sentiment.get('label', 'N/A').upper()} (polarity: {sentiment.get('polarity', 0):.2f})")
        lines.append(f"Market Relevance: {analysis.get('market_relevance', 0):.2f}")
        lines.append(f"Urgency: {analysis.get('urgency', 'N/A').upper()}")
        lines.append("")
        
        # Companies
        companies = analysis.get('companies', [])
        if companies:
            lines.append(f"COMPANIES MENTIONED ({len(companies)}):")
            for company in companies:
                lines.append(f"  - {company.get('name', 'N/A')} ({company.get('ticker', 'N/A')})")
                lines.append(f"    Sentiment: {company.get('sentiment', 'N/A')}")
                if company.get('reason'):
                    lines.append(f"    Reason: {company.get('reason', '')}")
            lines.append("")
        
        # Sectors & Topics
        if analysis.get('sectors'):
            lines.append(f"Sectors: {', '.join(analysis['sectors'])}")
        if analysis.get('topics'):
            lines.append(f"Topics: {', '.join(analysis['topics'])}")
        lines.append("")
        
        # AI Insights
        if analysis.get('ai_insights'):
            lines.append("AI INSIGHTS:")
            lines.append(analysis['ai_insights'])
            lines.append("")
        
        if analysis.get('risk_factors'):
            lines.append("RISK FACTORS:")
            lines.append(analysis['risk_factors'])
            lines.append("")
        
        # Trading Ideas
        if trading_ideas:
            lines.append("=" * 80)
            lines.append(f"TRADING IDEAS ({len(trading_ideas)})")
            lines.append("=" * 80)
            for i, idea in enumerate(trading_ideas, 1):
                lines.append(f"\n{i}. {idea['action']} {idea['ticker']}")
                if 'name' in idea:
                    lines.append(f"   Name: {idea['name']}")
                lines.append(f"   Type: {idea['type'].upper()}")
                lines.append(f"   Confidence: {idea['confidence'].upper()}")
                lines.append(f"   Risk: {idea['risk_level'].upper()}")
                lines.append(f"   Timeframe: {idea['timeframe']}")
                lines.append(f"   Rationale: {idea['rationale']}")
        else:
            lines.append("No specific trading ideas generated.")
        
        lines.append("\n" + "=" * 80)
        lines.append("DISCLAIMER: For informational purposes only. Not financial advice.")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _create_html_report(self, post: Dict, analysis: Dict, trading_ideas: List[Dict]) -> str:
        """Create HTML version of report"""
        # Handle both dict and string sentiment formats
        sentiment_data = analysis.get('sentiment', {})
        if isinstance(sentiment_data, dict):
            sentiment_label = sentiment_data.get('label', 'neutral')
            sentiment_score = sentiment_data.get('polarity', 0)
        else:
            sentiment_label = str(sentiment_data) if sentiment_data else 'neutral'
            sentiment_score = analysis.get('sentiment_score', 0)
        
        # Sentiment colors
        sentiment_colors = {
            'positive': '#28a745',
            'negative': '#dc3545',
            'neutral': '#6c757d'
        }
        sentiment_color = sentiment_colors.get(sentiment_label, '#6c757d')
        
        # Urgency colors
        urgency_colors = {
            'high': '#dc3545',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        urgency = analysis.get('urgency', 'low')
        urgency_color = urgency_colors.get(urgency, '#6c757d')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header p {{ margin: 5px 0 0 0; opacity: 0.9; }}
                .section {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #667eea; }}
                .section h2 {{ margin-top: 0; color: #667eea; font-size: 18px; }}
                .metric {{ display: inline-block; background: white; padding: 10px 15px; border-radius: 5px; margin: 5px; }}
                .metric-label {{ font-size: 12px; color: #6c757d; text-transform: uppercase; }}
                .metric-value {{ font-size: 20px; font-weight: bold; }}
                .company {{ background: white; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 3px solid {sentiment_color}; }}
                .company-header {{ font-weight: bold; font-size: 16px; }}
                .company-ticker {{ color: #667eea; font-weight: bold; }}
                .trading-idea {{ background: white; padding: 15px; border-radius: 8px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .trading-idea-header {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .badge {{ display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; margin: 0 5px; }}
                .badge-positive {{ background: #d4edda; color: #155724; }}
                .badge-negative {{ background: #f8d7da; color: #721c24; }}
                .badge-neutral {{ background: #e2e3e5; color: #383d41; }}
                .badge-high {{ background: #f8d7da; color: #721c24; }}
                .badge-medium {{ background: #fff3cd; color: #856404; }}
                .badge-low {{ background: #d4edda; color: #155724; }}
                .post-content {{ background: white; padding: 15px; border-radius: 5px; font-style: italic; color: #555; }}
                .footer {{ text-align: center; padding: 20px; color: #6c757d; font-size: 12px; }}
                a {{ color: #667eea; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚨 Trump Truth Social Trading Alert</h1>
                <p>{datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>📊 Analysis Summary</h2>
                <div class="metric">
                    <div class="metric-label">Sentiment</div>
                    <div class="metric-value" style="color: {sentiment_color};">{sentiment_label.upper()}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Market Relevance</div>
                    <div class="metric-value">{analysis.get('market_relevance', 0):.0%}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Urgency</div>
                    <div class="metric-value" style="color: {urgency_color};">{urgency.upper()}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📝 Post Content</h2>
                <div class="post-content">
                    {post.get('content', '')[:500]}
                    {'...' if len(post.get('content', '')) > 500 else ''}
                </div>
                <p style="margin-top: 10px;"><a href="{post.get('link', '#')}" target="_blank">View original post →</a></p>
            </div>
        """
        
        # Companies section
        companies = analysis.get('companies', [])
        if companies:
            html += """
            <div class="section">
                <h2>🏢 Companies Mentioned</h2>
            """
            for company in companies:
                comp_sentiment = company.get('sentiment', 'neutral')
                badge_class = f"badge-{comp_sentiment}"
                html += f"""
                <div class="company">
                    <div class="company-header">
                        <span class="company-ticker">{company.get('ticker', 'N/A')}</span> - {company.get('name', 'N/A')}
                        <span class="badge {badge_class}">{comp_sentiment.upper()}</span>
                    </div>
                    {f'<p style="margin: 5px 0 0 0; color: #666;">{company.get("reason", "")}</p>' if company.get('reason') else ''}
                </div>
                """
            html += "</div>"
        
        # Sectors & Topics
        if analysis.get('sectors') or analysis.get('topics'):
            html += '<div class="section"><h2>🎯 Sectors & Topics</h2>'
            if analysis.get('sectors'):
                html += f'<p><strong>Sectors:</strong> {", ".join(analysis["sectors"])}</p>'
            if analysis.get('topics'):
                html += f'<p><strong>Topics:</strong> {", ".join(analysis["topics"])}</p>'
            html += '</div>'
        
        # AI Insights
        if analysis.get('ai_insights'):
            html += f"""
            <div class="section">
                <h2>🤖 AI Insights</h2>
                <p>{analysis['ai_insights']}</p>
            </div>
            """
        
        # Risk Factors
        if analysis.get('risk_factors'):
            html += f"""
            <div class="section">
                <h2>⚠️ Risk Factors</h2>
                <p>{analysis['risk_factors']}</p>
            </div>
            """
        
        # Trading Ideas
        if trading_ideas:
            html += f"""
            <div class="section">
                <h2>💡 Trading Ideas ({len(trading_ideas)})</h2>
            """
            for i, idea in enumerate(trading_ideas, 1):
                confidence_colors = {'high': '#28a745', 'medium': '#ffc107', 'low': '#dc3545'}
                conf_color = confidence_colors.get(idea['confidence'], '#6c757d')
                
                html += f"""
                <div class="trading-idea">
                    <div class="trading-idea-header" style="color: {conf_color};">
                        {i}. {idea['action']} {idea['ticker']}
                        {f"({idea['name']})" if 'name' in idea else ''}
                    </div>
                    <p style="margin: 5px 0;">
                        <span class="badge badge-neutral">{idea['type'].upper()}</span>
                        <span class="badge" style="background: {conf_color}; color: white;">{idea['confidence'].upper()} CONFIDENCE</span>
                        <span class="badge badge-{idea['urgency'] if 'urgency' in idea else 'medium'}">{idea['risk_level'].upper()} RISK</span>
                    </p>
                    <p style="margin: 10px 0 5px 0;"><strong>Timeframe:</strong> {idea['timeframe']}</p>
                    <p style="margin: 5px 0;"><strong>Rationale:</strong> {idea['rationale']}</p>
                </div>
                """
            html += "</div>"
        
        html += """
            <div class="footer">
                <p><strong>DISCLAIMER:</strong> This is for informational and educational purposes only.<br>
                Not financial advice. Always do your own research and consult with financial advisors.</p>
            </div>
        </body>
        </html>
        """
        
        return html


def main():
    """Test email notification"""
    notifier = EmailNotifier()
    
    if not notifier.enabled:
        print("\nTo enable email notifications, add to your .env file:")
        print("SENDER_EMAIL=your_email@gmail.com")
        print("SENDER_PASSWORD=your_app_password")
        print("RECIPIENT_EMAIL=recipient@email.com")
        print("\nFor Gmail, use an App Password: https://myaccount.google.com/apppasswords")
        return
    
    # Test data
    test_post = {
        'content': 'BREAKING: Great meeting with Tim Cook today! Apple bringing iPhone production to USA!',
        'link': 'https://trumpstruth.org/test',
        'timestamp': datetime.now().isoformat()
    }
    
    test_analysis = {
        'sentiment': {'label': 'positive', 'polarity': 0.8},
        'market_relevance': 0.85,
        'urgency': 'high',
        'companies': [
            {'name': 'Apple', 'ticker': 'AAPL', 'sentiment': 'positive', 
             'reason': 'Bringing iPhone production to USA'}
        ],
        'sectors': ['Technology'],
        'topics': ['Manufacturing', 'Jobs'],
        'ai_insights': 'Strong positive signal for Apple stock.',
        'risk_factors': 'Claims need verification from Apple.'
    }
    
    test_ideas = [
        {
            'ticker': 'AAPL',
            'name': 'Apple',
            'action': 'Buy',
            'type': 'company',
            'confidence': 'high',
            'risk_level': 'medium',
            'timeframe': 'short-term',
            'urgency': 'high',
            'rationale': 'Positive mention suggests upside potential'
        }
    ]
    
    print("Sending test email...")
    success = notifier.send_analysis_report(test_post, test_analysis, test_ideas)
    
    if success:
        print("✓ Test email sent successfully!")
    else:
        print("✗ Failed to send test email")


if __name__ == "__main__":
    main()

