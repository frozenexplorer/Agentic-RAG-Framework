from __future__ import annotations
import json
from typing import Any, Dict, List
import numpy as np

from .llm_client import get_client
from .config import get_settings
from .index_store import IndexStore

TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search the company's internal policy documents. Use this whenever the user asks about company rules, benefits, leave, expenses, security, HR, or anything that should be grounded in internal docs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query, usually the user's question rewritten as keywords."},
                    "top_k": {"type": "integer", "description": "How many matching passages to return (1-8).", "default": 5},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    }
]

def search_docs(index: IndexStore, query: str, top_k: int = 5) -> Dict[str, Any]:
    s = get_settings()
    client = get_client()

    resp = client.embeddings.create(model=s.embedding_model, input=[query])
    qvec = np.array(resp.data[0].embedding, dtype=np.float32)

    results = index.search(qvec, top_k=top_k)
    out = []
    for score, meta in results:
        out.append({
            "score": round(score, 4),
            "chunk_id": meta["chunk_id"],
            "doc_id": meta["doc_id"],
            "source_path": meta["source_path"],
            "text": meta["text"],
        })

    return {
        "query": query,
        "top_k": top_k,
        "results": out,
        "notes": "Use results as citations. If results are irrelevant, say you could not find it in the provided docs.",
    }

def run_tool(index: IndexStore, name: str, arguments_json: str) -> str:
    """Execute a tool by name and return JSON string for the model."""
    try:
        args = json.loads(arguments_json or "{}")
    except json.JSONDecodeError:
        args = {}

    if name == "search_docs":
        query = str(args.get("query", "")).strip()
        top_k = int(args.get("top_k", get_settings().top_k))
        top_k = max(1, min(top_k, 8))
        if not query:
            return json.dumps({"error": "query is required"}, ensure_ascii=False)
        return json.dumps(search_docs(index, query=query, top_k=top_k), ensure_ascii=False)

    return json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False)
