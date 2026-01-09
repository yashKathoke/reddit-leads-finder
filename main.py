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
    'include': [],
    'exclude': []
}

SEMANTIC_FILTER_PARAMS = {
    'product_desc': "A tool for founders to automate Reddit lead discovery and social listening.",
    'threshold': 0.6
}

# --- Storage Paths ---
base_path = 'data/'
raw_posts_path = base_path+'main_raw_posts.json'
output_keyword_filter = base_path+'main_keyword_filter.json'
output_semantic_filter = base_path+'main_semantic_filter.json'



def main():
   collector = RedditCollector(storage_file=raw_posts_path)
   collector.run(SUBREDDITS)

   if ENABLE_KEYWORD_FILTER:
    keyword_filter = DynamicKeywordProcessor(raw_file=raw_posts_path, output_file=output_keyword_filter)
    keyword_filter.update_keywords(
        include= KEYWORD_FILTER_PARAMS['keywords'],
        exclude= KEYWORD_FILTER_PARAMS['exclude']
    )
    keyword_filter.process()

   if ENABLE_SEMANTIC_FILTER:
    semantic_filter = SemanticFilter(input_file=output_keyword_filter, output_file=output_semantic_filter)
    semantic_filter.filter(product_description=SEMANTIC_FILTER_PARAMS['product_desc'], threshold=SEMANTIC_FILTER_PARAMS['threshold'])
   

if __name__ == '__main__':
    main()