# src/agentic_rag/api.py
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

from .config import get_settings
from .index_store import IndexStore
from .memory import SessionMemory
from .agent import PolicyAgent

app = FastAPI(title="Agentic RAG Backend API")


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
    app.state.index = IndexStore.load(s.index_dir)
    app.state.agent = PolicyAgent(index=app.state.index)


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    s = app.state.settings
    agent: PolicyAgent = app.state.agent

    # Session-based memory only if session_id provided
    if req.session_id:
        mem = SessionMemory.load(s.sessions_dir, req.session_id)
        mem.add({"role": "user", "content": req.query})
        payload = agent.reply_with_sources(mem.messages)
        mem.add({"role": "assistant", "content": payload["answer"]})
        mem.save()
    else:
        # Stateless call
        payload = agent.reply_with_sources([{"role": "user", "content": req.query}])

    return AskResponse(answer=payload["answer"], source=payload["sources"])
