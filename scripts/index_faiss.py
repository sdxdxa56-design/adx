"""Script to index legal documents into a FAISS vector store.

Usage:
    python scripts/index_faiss.py --data-dir data/ --index-file faiss.index --meta-file metadata.json

This script uses sentence-transformers to embed text and faiss-cpu for indexing.
"""
import os
import argparse
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
import faiss

CHUNK_SIZE = 512
OVERLAP = 64


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def main(data_dir, index_file, meta_file, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    texts = []
    metas = []
    for p in Path(data_dir).glob("**/*.txt"):
        with open(p, 'r', encoding='utf-8') as f:
            text = f.read()
        chunks = chunk_text(text)
        for idx, c in enumerate(chunks):
            texts.append(c)
            metas.append({"source": str(p), "chunk": idx})

    print(f"Embedding {len(texts)} chunks with model {model_name}...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, index_file)

    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(metas, f, ensure_ascii=False, indent=2)

    print(f"Wrote index to {index_file} and metadata to {meta_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', default='data')
    parser.add_argument('--index-file', default='faiss.index')
    parser.add_argument('--meta-file', default='metadata.json')
    parser.add_argument('--model', default='all-MiniLM-L6-v2')
    args = parser.parse_args()
    main(args.data_dir, args.index_file, args.meta_file, model_name=args.model)