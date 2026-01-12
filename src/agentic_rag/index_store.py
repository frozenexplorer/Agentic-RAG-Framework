from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple
import json
import numpy as np

try:
    import faiss
except Exception as e:
    raise ImportError(
        "FAISS is required. Install with: pip install faiss-cpu"
    ) from e


@dataclass
class IndexStore:
    index: "faiss.Index"
    meta: List[Dict[str, Any]]

    @classmethod
    def load(cls, index_dir: Path) -> "IndexStore":
        faiss_path = index_dir / "faiss.index"
        meta_path = index_dir / "meta.jsonl"
        if not faiss_path.exists() or not meta_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found in {index_dir}. Run: python -m agentic_rag.index"
            )

        index = faiss.read_index(str(faiss_path))

        meta = []
        with meta_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    meta.append(json.loads(line))

        return cls(index=index, meta=meta)

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        # cosine similarity via inner product on normalized vectors
        q = query_vec.astype(np.float32).reshape(1, -1)
        faiss.normalize_L2(q)

        top_k = max(1, min(int(top_k), len(self.meta)))
        scores, ids = self.index.search(q, top_k)

        out: List[Tuple[float, Dict[str, Any]]] = []
        for score, i in zip(scores[0].tolist(), ids[0].tolist()):
            if i == -1:
                continue
            out.append((float(score), self.meta[i]))
        return out
