"""
ARK Invest Daily Trades Scraper

Fetches daily trading activity from ARK Invest's official API.
Cathie Wood's trades are highly influential in tech/innovation stocks.
"""

import requests
from datetime import datetime
from typing import List, Dict, Optional
import time


class ARKTradesScraper:
    def __init__(self):
        self.base_url = "https://arkfunds.io/api/v2/etf/trades"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # ARK ETF symbols to monitor
        self.etf_symbols = ['ARKK', 'ARKG', 'ARKW', 'ARKF', 'ARKQ', 'ARKX']
        
    def fetch_latest_trades(self, limit: int = 10) -> List[Dict]:
        """
        Fetch latest trades from ARK Invest API for all ETFs
        
        Args:
            limit: Maximum number of trades to fetch per ETF
            
        Returns:
            List of trade dictionaries
        """
        all_trades = []
        
        for symbol in self.etf_symbols:
            try:
                print(f"[INFO] Fetching {symbol} trades from API...")
                
                params = {
                    'symbol': symbol,
                    'limit': limit
                }
                
                response = self.session.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                
                trades_data = response.json()
                
                # Parse and normalize the trades
                for trade in trades_data.get('trades', []):
                    normalized_trade = self._normalize_trade(trade)
                    if normalized_trade:
                        all_trades.append(normalized_trade)
                
                print(f"[OK] Fetched {len(trades_data.get('trades', []))} trades from {symbol}")
                
                # Small delay between requests to be polite
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"[WARNING] Failed to fetch {symbol} trades: {e}")
                continue
            except Exception as e:
                print(f"[WARNING] Unexpected error fetching {symbol} trades: {e}")
                continue
        
        print(f"[OK] Total: Fetched {len(all_trades)} ARK trades across all funds")
        return all_trades
    
    def _normalize_trade(self, trade: Dict) -> Optional[Dict]:
        """
        Normalize trade data to consistent format
        
        Expected ARK API format:
        {
            "date": "2024-01-15",
            "fund": "ARKK",
            "ticker": "TSLA",
            "company": "Tesla Inc",
            "cusip": "88160R101",
            "direction": "Buy" or "Sell",
            "shares": 150000,
            "etf_percent": 0.52
        }
        """
        try:
            # Generate unique ID from trade details
            trade_id = f"ark_{trade.get('date')}_{trade.get('fund')}_{trade.get('ticker')}_{trade.get('direction')}"
            
            # Normalize direction
            direction = trade.get('direction', '').lower()
            if direction not in ['buy', 'sell']:
                return None
            
            # Parse date
            date_str = trade.get('date', '')
            try:
                trade_date = datetime.strptime(date_str, '%Y-%m-%d')
                timestamp = trade_date.isoformat()
            except:
                timestamp = datetime.now().isoformat()
            
            # Get share count and percentage
            shares = trade.get('shares', 0)
            etf_percent = trade.get('etf_percent', 0)
            
            # Build normalized trade object
            normalized = {
                'id': trade_id,
                'source': 'ARK_INVEST',
                'timestamp': timestamp,
                'date': date_str,
                'fund': trade.get('fund', ''),
                'ticker': trade.get('ticker', ''),
                'company': trade.get('company', ''),
                'cusip': trade.get('cusip', ''),
                'direction': direction,
                'shares': shares,
                'etf_percent': etf_percent,
                'trader': 'Cathie Wood (ARK Invest)',
                'link': f"https://arkfunds.io/trades/{trade.get('fund', '').lower()}",
                
                # For compatibility with existing analyzer
                'title': f"ARK {direction.upper()}: {trade.get('ticker')} ({trade.get('company')})",
                'content': self._generate_content(trade, direction, shares, etf_percent),
                'type': 'trade'
            }
            
            return normalized
            
        except Exception as e:
            print(f"[WARNING] Failed to normalize trade: {e}")
            return None
    
    def _generate_content(self, trade: Dict, direction: str, shares: int, etf_percent: float) -> str:
        """Generate readable content from trade data"""
        fund = trade.get('fund', '')
        ticker = trade.get('ticker', '')
        company = trade.get('company', '')
        
        # Format share count
        if shares >= 1_000_000:
            shares_str = f"{shares/1_000_000:.2f}M"
        elif shares >= 1_000:
            shares_str = f"{shares/1_000:.1f}K"
        else:
            shares_str = str(shares)
        
        # Build content
        action = "bought" if direction == "buy" else "sold"
        content = f"Cathie Wood's {fund} {action} {shares_str} shares of {ticker} ({company})"
        
        if etf_percent:
            content += f", representing {etf_percent:.2f}% of the fund"
        
        return content
    
    def get_fund_summary(self, trades: List[Dict]) -> Dict:
        """
        Get summary of trading activity by fund
        
        Args:
            trades: List of normalized trades
            
        Returns:
            Dictionary with fund-level statistics
        """
        summary = {}
        
        for trade in trades:
            fund = trade.get('fund', 'UNKNOWN')
            if fund not in summary:
                summary[fund] = {
                    'buys': [],
                    'sells': [],
                    'total_buys': 0,
                    'total_sells': 0
                }
            
            direction = trade.get('direction')
            ticker = trade.get('ticker')
            shares = trade.get('shares', 0)
            
            if direction == 'buy':
                summary[fund]['buys'].append(ticker)
                summary[fund]['total_buys'] += shares
            elif direction == 'sell':
                summary[fund]['sells'].append(ticker)
                summary[fund]['total_sells'] += shares
        
        return summary


if __name__ == "__main__":
    # Test the scraper
    print("=" * 80)
    print("ARK Invest Trades Scraper Test")
    print("=" * 80)
    
    scraper = ARKTradesScraper()
    trades = scraper.fetch_latest_trades(limit=10)
    
    if trades:
        print(f"\n[OK] Successfully fetched {len(trades)} trades\n")
        
        for i, trade in enumerate(trades, 1):
            print(f"{i}. {trade['title']}")
            print(f"   Date: {trade['date']}")
            print(f"   Fund: {trade['fund']}")
            print(f"   Shares: {trade['shares']:,}")
            print(f"   Direction: {trade['direction'].upper()}")
            print(f"   Content: {trade['content']}")
            print()
        
        # Show summary
        summary = scraper.get_fund_summary(trades)
        print("\n" + "=" * 80)
        print("FUND SUMMARY")
        print("=" * 80)
        for fund, stats in summary.items():
            print(f"\n{fund}:")
            if stats['buys']:
                print(f"  Buys: {', '.join(stats['buys'])} ({stats['total_buys']:,} shares)")
            if stats['sells']:
                print(f"  Sells: {', '.join(stats['sells'])} ({stats['total_sells']:,} shares)")
    else:
        print("[ERROR] No trades fetched")

