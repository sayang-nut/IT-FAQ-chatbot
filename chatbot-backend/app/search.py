# app/search.py
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
THRESHOLD = 0.4
TOP_K = 3

class SemanticSearch:
    def __init__(self, kb_path: str = "knowledge_base.json"):
        print("[Search] Loading model...")
        self.model = SentenceTransformer(MODEL_NAME)

        print("[Search] Loading knowledge base...")
        with open(kb_path, encoding="utf-8") as f:
            self.kb = json.load(f)

        # Mỗi item encode = question + keywords ghép lại
        # Giúp tìm được cả khi user dùng từ đồng nghĩa với keyword
        corpus = [
            item["question"] + " " + " ".join(item["keywords"])
            for item in self.kb
        ]

        print("[Search] Encoding knowledge base...")
        self.embeddings = self.model.encode(corpus, normalize_embeddings=True)
        print(f"[Search] Ready — {len(self.kb)} items loaded.")

    def find(self, query: str) -> list[dict]:
        query_vec = self.model.encode([query], normalize_embeddings=True)

        # normalize_embeddings=True → cosine similarity = dot product
        scores = np.dot(self.embeddings, query_vec.T).flatten()

        top_indices = scores.argsort()[-TOP_K:][::-1]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score >= THRESHOLD:
                results.append({
                    "item": self.kb[idx],
                    "score": round(score, 4)
                })

        return results