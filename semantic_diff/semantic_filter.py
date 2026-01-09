"""
LeadMiner AI - Semantic Filter (Phase 3)
Uses local AI embeddings to find leads based on meaning, not just words.
"""

import json
import os
from sentence_transformers import SentenceTransformer, util

class SemanticFilter:
    def __init__(self, model_name='all-MiniLM-L6-v2', input_file="data/filtered_posts.json"):
        self.input_file = input_file
        self.output_file = "data/semantic_leads.json"
        
        # This downloads the model on the first run (local hereafter)
        print(f"[*] Loading local AI model ({model_name})...")
        self.model = SentenceTransformer(model_name)

    def filter(self, product_description: str, threshold: float = 0.4) -> int:
        """
        Calculates similarity between your product and the filtered Reddit posts.
        """
        if not os.path.exists(self.input_file):
            print("[!] No filtered posts found. Run Phase 2 first.")
            return 0

        with open(self.input_file, 'r') as f:
            posts = json.load(f)

        if not posts:
            return 0

        # 1. Encode your product description once
        product_embedding = self.model.encode(product_description, convert_to_tensor=True)

        # 2. Encode all post titles/summaries in a batch (very fast)
        post_texts = [f"{p['title']} {p['summary']}" for p in posts]
        post_embeddings = self.model.encode(post_texts, convert_to_tensor=True)

        # 3. Compute Cosine Similarity
        cosine_scores = util.cos_sim(product_embedding, post_embeddings)[0]

        semantic_leads = []
        for i, score in enumerate(cosine_scores):
            # Only keep leads that are "semantically close" to your product
            if score >= threshold:
                post = posts[i]
                post['semantic_score'] = float(score)
                semantic_leads.append(post)

        # Sort by best match first
        semantic_leads.sort(key=lambda x: x['semantic_score'], reverse=True)

        with open(self.output_file, 'w') as f:
            json.dump(semantic_leads, f, indent=4)

        return len(semantic_leads)

if __name__ == "__main__":
    # Example: Describe your product naturally
    MY_PRODUCT = "A tool for founders to automate Reddit lead discovery and social listening."
    
    filterer = SemanticFilter()
    count = filterer.filter(product_description=MY_PRODUCT, threshold=0.35)
    
    print(f"--- Semantic Analysis Complete ---")
    print(f"[✔] Found {count} leads that semantically match your product.")