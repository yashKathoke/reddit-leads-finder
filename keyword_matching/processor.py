"""
LeadMiner AI - Dynamic Keyword Processor
Supports LLM-generated keywords and real-time user input.
"""

import json
import re
import os
from typing import List, Dict, Optional

class DynamicKeywordProcessor:
    def __init__(self, raw_file="data/raw_posts.json", output_file="data/filtered_posts.json"):
        self.raw_file = raw_file
        self.output_file = output_file
        
        # Internal state for keywords
        self.intent_keywords = []
        self.negative_keywords = []
        
        # Pre-compiled regex objects
        self._include_re = None
        self._exclude_re = None

    def update_keywords(self, include: List[str], exclude: List[str]):
        """
        Dynamically update the filtering engine. 
        Call this when your LLM generates new target phrases.
        """
        self.intent_keywords = [k.strip().lower() for k in include if k.strip()]
        self.negative_keywords = [k.strip().lower() for k in exclude if k.strip()]
        
        # Re-compile patterns with word boundaries for precision
        if self.intent_keywords:
            pattern = r'\b(' + '|'.join(map(re.escape, self.intent_keywords)) + r')\b'
            self._include_re = re.compile(pattern, re.IGNORECASE)
        
        if self.negative_keywords:
            pattern = r'\b(' + '|'.join(map(re.escape, self.negative_keywords)) + r')\b'
            self._exclude_re = re.compile(pattern, re.IGNORECASE)

    def process(self) -> int:
        if not os.path.exists(self.raw_file):
            return 0
        
        # Fallback to defaults if no keywords provided
        if not self._include_re:
            print("[!] No keywords set. Skipping process.")
            return 0

        with open(self.raw_file, 'r') as f:
            posts = json.load(f)

        filtered_leads = []
        for post in posts:
            full_text = f"{post['title']} {post['summary']}"
            
            # Check for blocklist first (Efficiency Hack)
            if self._exclude_re and self._exclude_re.search(full_text):
                continue
                
            # Check for intent
            match = self._include_re.search(full_text)
            if match:
                # Find all unique matches to calculate a "Keyword Density Score"
                found = list(set(self._include_re.findall(full_text)))
                post['matches'] = found
                post['keyword_score'] = len(found)
                filtered_leads.append(post)

        # Atomic Save
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w') as f:
            json.dump(filtered_leads, f, indent=4)

        return len(filtered_leads)

# --- EXAMPLE INTEGRATION (LLM + USER INPUT) ---
if __name__ == "__main__":
    # 1. User Input from your future UI
    user_subs = ["looking for", "alternative to"]
    
    # 2. Simulated LLM Output (Gemini could suggest these based on product)
    llm_suggestions = ["how do I", "is there a tool", "best way to"]
    
    processor = DynamicKeywordProcessor()
    
    # Combine and update
    processor.update_keywords(
        include=user_subs + llm_suggestions,
        exclude=["hiring", "job", "recruiting"]
    )
    
    count = processor.process()
    print(f"[✔] Dynamic filtering complete. Found {count} leads.")