"""
Reddit Intelligence Collector - 2026 Stealth Edition
Includes: Fingerprint rotation, Jittered delays, and Proxy support.
"""

import feedparser
import json
import os
import random
import time
import argparse
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup


# PROVEN 2026 BROWSER FINGERPRINTS
# These include modern headers like Sec-CH-UA which Reddit's WAF checks
BROWSER_PROFILES = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-CH-UA": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Sec-CH-UA-Platform": '"macOS"'
    }
]

class RedditCollector:
    def __init__(self, storage_file: str = "raw_posts.json", proxy: str = None):
        self.storage_file = storage_file
        self.proxy = proxy # Format: "http://user:pass@host:port"
        self.data = self._load_existing_data()

    def _load_existing_data(self) -> List[Dict]:
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError: return []
        return []

    def fetch(self, subreddit: str, feed_type: str = "new", limit: int = 50) -> List[Dict]:
        url = f"https://www.reddit.com/r/{subreddit}/{feed_type}/.rss?limit={limit}&cb={random.randint(1, 9999)}"
        
        # Select a random browser profile for this request
        profile = random.choice(BROWSER_PROFILES)
        
        # feedparser uses 'agent' for UA, but we can pass extra headers in 'request_headers'
        # Note: If using proxies, pass them into feedparser's handlers (requires advanced setup)
        feed = feedparser.parse(url, agent=profile["User-Agent"], request_headers=profile)
        
        if hasattr(feed, 'status'):
            if feed.status == 429:
                wait = random.randint(300, 600)
                print(f"[!!!] Rate Limit (429). Cool-down: {wait}s")
                time.sleep(wait)
                return []
            if feed.status == 403:
                print(f"[!!!] Access Forbidden (403). Your IP may be flagged.")
                return []

        posts = []
        for entry in feed.entries:
            raw_html = entry.get("summary", "")

            soap = BeautifulSoup(raw_html, "html.parser")
            clean_text = soap.get_text(separator=" ", strip=True)

            posts.append({
                "id": entry.id,
                "title": entry.title,
                "link": entry.link,
                "summary": entry.summary,
                "subreddit": subreddit,
                "captured_at": datetime.now().isoformat()
            })
        return posts

    def save(self, new_posts: List[Dict]):
        seen_ids = {p['id'] for p in self.data}
        added = 0
        for p in new_posts:
            if p['id'] not in seen_ids:
                self.data.append(p)
                seen_ids.add(p['id'])
                added += 1
        
        with open(self.storage_file, 'w') as f:
            json.dump(self.data, f, indent=4)
        return added

def main():
    parser = argparse.ArgumentParser(description="🚀 Stealth Reddit Collector")
    parser.add_argument("--subs", nargs="+", default=["startups", "saas"])
    parser.add_argument("--delay", type=int, default=15, help="Base delay between subs")
    args = parser.parse_args()
    
    collector = RedditCollector()
    
    for sub in args.subs:
        # HUMAN JITTER: Randomly wait BEFORE request to break patterns
        jitter = random.uniform(args.delay * 0.5, args.delay * 1.5)
        print(f"[*] Mimicking human pause: {jitter:.2f}s...")
        time.sleep(jitter)
        
        posts = collector.fetch(sub)
        added = collector.save(posts)
        print(f"[+] r/{sub}: Found {len(posts)}, Added {added}")

if __name__ == "__main__":
    main()