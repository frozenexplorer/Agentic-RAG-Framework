# backend/agentic_rag/api.py
from __future__ import annotations

from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import get_settings
from .index_store import IndexStore
from .memory import SessionMemory
from .agent import PolicyAgent

app = FastAPI(title="Agentic RAG App")


class AskRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    source: List[str]


@app.on_event("startup")
def _startup():
    s = get_settings()
    app.state.settings = s

    # If FAISS index is missing inside the container, build it from data/docs
    try:
        app.state.index = IndexStore.load(s.index_dir)
    except FileNotFoundError:
        from .index import build_index  # import here to avoid circular imports
        build_index()
        app.state.index = IndexStore.load(s.index_dir)

    app.state.agent = PolicyAgent(index=app.state.index)



@app.get("/health", include_in_schema=False)
def health():
    return {"ok": True}


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    s = app.state.settings
    agent: PolicyAgent = app.state.agent

    # Session-based memory only if session_id provided
    if req.session_id:
        mem = SessionMemory.load(s.sessions_dir, req.session_id)
        mem.add({"role": "user", "content": req.query})
        payload = await agent.reply_with_sources(mem.messages)
        mem.add({"role": "assistant", "content": payload["answer"]})
        mem.save()
    else:
        # Stateless call
        payload = await agent.reply_with_sources([{"role": "user", "content": req.query}])

    return AskResponse(answer=payload["answer"], source=payload["sources"])


# ---------------------------
# Serve React build (single URL)
# ---------------------------
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Prefer container path first
DIST_DIR = Path("/app/frontend/dist")
if not DIST_DIR.exists():
    # Local dev path fallback (repo root = .../Agentic-RAG-Framework)
    REPO_ROOT = Path(__file__).resolve().parents[3]
    DIST_DIR = REPO_ROOT / "frontend" / "dist"

if DIST_DIR.exists():
    assets_dir = DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/", include_in_schema=False)
    def serve_root():
        return FileResponse(str(DIST_DIR / "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        # Don't hijack API or asset routes
        if full_path.startswith(("ask", "health", "docs", "openapi.json", "assets")):
            return {"detail": "Not Found"}
        return FileResponse(str(DIST_DIR / "index.html"))

