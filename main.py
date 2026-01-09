import json
from collector.collector import RedditCollector
from keyword_matching.processor import DynamicKeywordProcessor
from semantic_diff.semantic_filter import SemanticFilter

# --- Configuration ---
SUBREDDITS = ['SaaS', 'startups']
POSTS_LIMIT = 50
SORT_BY = 'new'  # 'hot', 'new', 'top', 'rising'

# --- Filter Switches ---
ENABLE_KEYWORD_FILTER = True
ENABLE_SEMANTIC_FILTER = False

# --- Filter Parameters ---
KEYWORD_FILTER_PARAMS = {
    'keywords': ['hiring', 'job', 'remote', 'apply']
}
SEMANTIC_FILTER_PARAMS = {
    'threshold': 0.6
}

# --- Storage Paths ---
base_path = 'data/'
raw_posts_path = base_path+'main_raw_posts.json'



def main():
   collector = RedditCollector(storage_file=raw_posts_path)
   collector.run(SUBREDDITS)

if __name__ == '__main__':
    main()