from __future__ import annotations
import json
from typing import Any, Dict, List
import numpy as np

from .llm_client import get_async_client
from .config import get_settings
from .index_store import IndexStore

TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search the company's internal policy documents using semantic similarity. Use this whenever the user asks about company rules, benefits, leave, expenses, security, HR, POSH (Prevention of Sexual Harassment), compliance, or any policy-related topic. The search uses embeddings to find semantically similar content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query, usually the user's question rewritten as keywords."},
                    "top_k": {"type": "integer", "description": "How many matching passages to return (1-10).", "default": 8},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    }
]

async def search_docs(index: IndexStore, query: str, top_k: int = 8) -> Dict[str, Any]:
    s = get_settings()
    client = get_async_client()

    resp = await client.embeddings.create(model=s.embedding_model, input=[query])
    qvec = np.array(resp.data[0].embedding, dtype=np.float32)

    results = index.search(qvec, top_k=top_k)
    
    # Filter out low-relevance results (semantic filtering)
    RELEVANCE_THRESHOLD = 0.5
    out = []
    for score, meta in results:
        # Only include results above relevance threshold
        if score >= RELEVANCE_THRESHOLD:
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
        "num_results": len(out),
        "results": out,
        "notes": "Results are sorted by relevance score (0-1). Higher scores = more relevant. Only results with score >= 0.5 are shown. If no results or low scores, the information is not in the documents.",
    }

async def run_tool(index: IndexStore, name: str, arguments_json: str) -> str:
    """Execute a tool by name and return JSON string for the model."""
    try:
        args = json.loads(arguments_json or "{}")
    except json.JSONDecodeError:
        args = {}

    if name == "search_docs":
        query = str(args.get("query", "")).strip()
        top_k = int(args.get("top_k", get_settings().top_k))
        top_k = max(1, min(top_k, 10))
        if not query:
            return json.dumps({"error": "query is required"}, ensure_ascii=False)
        return json.dumps(await search_docs(index, query=query, top_k=top_k), ensure_ascii=False)

    return json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False)
