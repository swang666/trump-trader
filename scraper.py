"""
Truth Social Post Scraper
Fetches real-time posts from trumpstruth.org
"""

import requests
from bs4 import BeautifulSoup
import feedparser
import time
from datetime import datetime
import json
from typing import List, Dict, Optional


class TruthSocialScraper:
    """Scrapes Trump's Truth Social posts from trumpstruth.org"""
    
    def __init__(self):
        self.base_url = "https://trumpstruth.org"
        self.rss_url = "https://trumpstruth.org/feed/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.last_post_id = None
        
    def fetch_latest_posts(self, limit: int = 10) -> List[Dict]:
        """
        Fetch the latest posts from Truth Social via RSS feed
        
        Args:
            limit: Maximum number of posts to fetch
            
        Returns:
            List of post dictionaries
        """
        try:
            # Try RSS feed first
            posts = self._fetch_from_rss(limit)
            if posts:
                return posts
            
            # Fallback to web scraping
            return self._fetch_from_web(limit)
            
        except Exception as e:
            print(f"Error fetching posts: {e}")
            return []
    
    def _fetch_from_rss(self, limit: int) -> List[Dict]:
        """Fetch posts from RSS feed"""
        try:
            feed = feedparser.parse(self.rss_url)
            posts = []
            
            for entry in feed.entries[:limit]:
                post = {
                    'id': entry.get('id', entry.get('link', '')),
                    'content': entry.get('summary', entry.get('description', '')),
                    'title': entry.get('title', ''),
                    'timestamp': self._parse_timestamp(entry.get('published', '')),
                    'link': entry.get('link', ''),
                    'source': 'rss'
                }
                posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"RSS fetch failed: {e}")
            return []
    
    def _fetch_from_web(self, limit: int) -> List[Dict]:
        """Fallback web scraping method"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = []
            
            # Look for post containers (adjust selectors based on actual site structure)
            post_elements = soup.find_all(['article', 'div'], class_=['post', 'entry', 'truth'], limit=limit)
            
            for idx, element in enumerate(post_elements):
                # Extract post content
                content_elem = element.find(['p', 'div'], class_=['content', 'entry-content', 'post-content'])
                content = content_elem.get_text(strip=True) if content_elem else ''
                
                # Extract timestamp
                time_elem = element.find(['time', 'span'], class_=['date', 'timestamp', 'published'])
                timestamp = time_elem.get('datetime', '') if time_elem else ''
                
                # Extract link
                link_elem = element.find('a', href=True)
                link = link_elem['href'] if link_elem else ''
                if link and not link.startswith('http'):
                    link = self.base_url + link
                
                post = {
                    'id': link or f"post_{idx}_{int(time.time())}",
                    'content': content,
                    'title': '',
                    'timestamp': self._parse_timestamp(timestamp),
                    'link': link,
                    'source': 'web'
                }
                
                if content:  # Only add if we got content
                    posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"Web scraping failed: {e}")
            return []
    
    def get_new_posts(self) -> List[Dict]:
        """
        Get only new posts since last check
        
        Returns:
            List of new post dictionaries
        """
        all_posts = self.fetch_latest_posts(limit=20)
        
        if not all_posts:
            return []
        
        # If this is the first run, just return the latest post
        if self.last_post_id is None:
            self.last_post_id = all_posts[0]['id']
            return [all_posts[0]]
        
        # Find new posts
        new_posts = []
        for post in all_posts:
            if post['id'] == self.last_post_id:
                break
            new_posts.append(post)
        
        # Update last seen post
        if new_posts:
            self.last_post_id = new_posts[0]['id']
        
        return new_posts
    
    def _parse_timestamp(self, timestamp_str: str) -> str:
        """Parse and normalize timestamp"""
        if not timestamp_str:
            return datetime.now().isoformat()
        
        try:
            # Try parsing common formats
            from dateutil import parser
            dt = parser.parse(timestamp_str)
            return dt.isoformat()
        except:
            return datetime.now().isoformat()
    
    def test_connection(self) -> bool:
        """Test if we can connect to trumpstruth.org"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            return response.status_code == 200
        except:
            return False


def main():
    """Test the scraper"""
    scraper = TruthSocialScraper()
    
    print("Testing connection to trumpstruth.org...")
    if scraper.test_connection():
        print("✓ Connection successful")
    else:
        print("✗ Connection failed")
    
    print("\nFetching latest posts...")
    posts = scraper.fetch_latest_posts(limit=5)
    
    if posts:
        print(f"\nFound {len(posts)} posts:\n")
        for i, post in enumerate(posts, 1):
            print(f"{i}. [{post['timestamp']}]")
            print(f"   Content: {post['content'][:100]}...")
            print(f"   Link: {post['link']}\n")
    else:
        print("No posts found")


if __name__ == "__main__":
    main()

