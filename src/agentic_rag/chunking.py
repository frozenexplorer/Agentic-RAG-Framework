from __future__ import annotations
from typing import List, Dict, Any
import tiktoken

def _get_encoding():
    # Prefer newer encoding when available; fall back safely.
    for name in ("o200k_base", "cl100k_base"):
        try:
            return tiktoken.get_encoding(name)
        except Exception:
            continue
    return tiktoken.get_encoding("cl100k_base")

def chunk_text(text: str, *, chunk_tokens: int = 800, overlap: int = 120) -> List[Dict[str, Any]]:
    """Token-aware chunking. Returns list of {text, start_tok, end_tok}."""
    enc = _get_encoding()
    toks = enc.encode(text)
    chunks = []
    i = 0
    n = len(toks)
    if chunk_tokens <= 0:
        raise ValueError("chunk_tokens must be > 0")
    if overlap >= chunk_tokens:
        raise ValueError("overlap must be < chunk_tokens")

    while i < n:
        j = min(i + chunk_tokens, n)
        chunk = enc.decode(toks[i:j]).strip()
        if chunk:
            chunks.append({"text": chunk, "start_tok": i, "end_tok": j})
        if j == n:
            break
        i = j - overlap
    return chunks
