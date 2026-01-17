# src/agentic_rag/index.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import numpy as np

# FAISS (local, free vector store)
try:
    import faiss  # type: ignore
except Exception as e:
    raise ImportError(
        "FAISS is required for Task 2 storage. Install with:\n"
        "  pip install faiss-cpu\n"
    ) from e

from .config import get_settings
from .llm_client import get_client
from .docs_loader import iter_docs
from .chunking import chunk_text


def _batched(items: List[str], batch_size: int):
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]


def build_index() -> None:
    s = get_settings()
    client = get_client()

    # 1) Load + chunk docs
    chunks = []
    for doc in iter_docs(s.docs_dir):
        for k, ch in enumerate(
            chunk_text(doc["text"], chunk_tokens=s.chunk_tokens, overlap=s.chunk_overlap)
        ):
            chunks.append(
                {
                    "doc_id": doc["doc_id"],
                    "source_path": doc["path"],
                    "chunk_id": f"{doc['doc_id']}::chunk_{k}",
                    "text": ch["text"],
                    "start_tok": ch["start_tok"],
                    "end_tok": ch["end_tok"],
                }
            )

    if not chunks:
        raise SystemExit(f"No supported documents found in {s.docs_dir} (txt/md/pdf).")

    # 2) Embed in batches
    texts = [c["text"].replace("\n", " ") for c in chunks]
    vectors: List[List[float]] = []

    for batch in _batched(texts, batch_size=64):
        resp = client.embeddings.create(model=s.embedding_model, input=batch)
        vectors.extend([d.embedding for d in resp.data])

    emb = np.array(vectors, dtype=np.float32)
    if emb.shape[0] != len(chunks):
        raise RuntimeError("Embedding count mismatch.")

    # 3) Build + persist FAISS index (cosine similarity using inner product on L2-normalized vectors)
    s.index_dir.mkdir(parents=True, exist_ok=True)

    # Normalize in-place for cosine similarity
    faiss.normalize_L2(emb)

    # IndexFlatIP = exact inner-product search
    index = faiss.IndexFlatIP(emb.shape[1])
    index.add(emb)

    faiss_path = s.index_dir / "faiss.index"
    faiss.write_index(index, str(faiss_path))

    # (Optional) also save raw embeddings for debugging/inspection
    np.save(str(s.index_dir / "embeddings.npy"), emb)

    # 4) Persist metadata (one line per chunk)
    meta_path = s.index_dir / "meta.jsonl"
    with meta_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            c2 = dict(c)
            # Keep tool payload smaller (optional)
            if len(c2["text"]) > 2000:
                c2["text"] = c2["text"][:2000] + "…"
            f.write(json.dumps(c2, ensure_ascii=False) + "\n")

    # 5) Manifest
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provider": s.provider,
        "embedding_model": s.embedding_model,
        "num_chunks": len(chunks),
        "dim": int(emb.shape[1]),
        "chunk_tokens": s.chunk_tokens,
        "chunk_overlap": s.chunk_overlap,
        "vector_store": "faiss",
        "faiss_index_type": "IndexFlatIP",
        "files": {
            "faiss_index": str(faiss_path),
            "meta": str(meta_path),
            "embeddings_npy": str(s.index_dir / "embeddings.npy"),
        },
    }
    (s.index_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    print(f"✅ Indexed {len(chunks)} chunks from {s.docs_dir}")
    print(f"✅ Saved FAISS index to {faiss_path}")
    print(f"✅ Saved metadata to {meta_path}")


if __name__ == "__main__":
    build_index()
