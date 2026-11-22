
import os

# Set thread limits before importing PyTorch or NumPy.
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import json
from pathlib import Path

import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer


torch.set_num_threads(1)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

EVIDENCE_PATH = DATA_DIR / "evidence.json"
INDEX_PATH = DATA_DIR / "evidence.index"
METADATA_PATH = DATA_DIR / "vector_metadata.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_model():
    print(f"Loading embedding model: {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME, device="cpu")


def build_index():
    with EVIDENCE_PATH.open("r", encoding="utf-8") as file:
        evidence = json.load(file)

    records = evidence.get("records", [])

    if not records:
        raise ValueError("No evidence records available.")

    texts = [record["raw_line"] for record in records]

    model = load_model()

    print(f"Generating embeddings for {len(texts)} records...")

    embeddings = model.encode(
        texts,
        batch_size=1,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    embeddings = np.asarray(embeddings, dtype=np.float32)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))

    with METADATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    print("\nVector index successfully created.")
    print(f"Records indexed: {index.ntotal}")
    print(f"Embedding dimensions: {embeddings.shape[1]}")


def semantic_search(query, top_k=5):
    if not query.strip():
        return []

    if not INDEX_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Run python -m retrieval.vector_store first."
        )

    index = faiss.read_index(str(INDEX_PATH))

    with METADATA_PATH.open("r", encoding="utf-8") as file:
        records = json.load(file)

    model = load_model()

    query_embedding = model.encode(
        [query],
        batch_size=1,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    scores, indices = index.search(
        query_embedding,
        min(top_k, index.ntotal)
    )

    results = []

    for score, record_index in zip(scores[0], indices[0]):
        if record_index >= 0:
            results.append({
                "score": float(score),
                "record": records[int(record_index)]
            })

    return results


if __name__ == "__main__":
    build_index()
