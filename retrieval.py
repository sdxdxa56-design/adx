"""Simple retrieval module to query FAISS and return top-k relevant chunks.

Usage:
    from retrieval import Retriever
    r = Retriever('faiss.index', 'metadata.json')
    r.query('نص السؤال', top_k=3)
"""
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


class Retriever:
    def __init__(self, index_path='faiss.index', meta_path='metadata.json', model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = faiss.read_index(index_path)
        with open(meta_path, 'r', encoding='utf-8') as f:
            self.meta = json.load(f)

    def query(self, text, top_k=3):
        emb = self.model.encode([text], convert_to_numpy=True)
        D, I = self.index.search(emb, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            m = self.meta[idx]
            results.append({'score': float(score), 'source': m['source'], 'chunk': m['chunk']})
        return results
